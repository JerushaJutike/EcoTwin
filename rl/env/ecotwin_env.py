from __future__ import annotations

from pathlib import Path

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import traci

from rl.env.reward import calculate_reward
from rl.env.state import collect_intersection_state


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SUMO_CONFIG = (
    PROJECT_ROOT
    / "simulation"
    / "config"
    / "ecotwin.sumocfg"
)

TLS_ID = "B1"

GREEN_EW = 0
YELLOW_EW_TO_NS = 1

GREEN_NS = 2
YELLOW_NS_TO_EW = 3

YELLOW_DURATION = 3

# Every RL action represents exactly 15 seconds
# of simulated time.
DECISION_INTERVAL = 15


class EcoTwinEnv(gym.Env):
    """
    Gymnasium environment controlling intersection B1.

    Actions
    -------
    0:
        East/West green.

    1:
        North/South green.

    Observation
    -----------
    13-dimensional vector:

    4 queue lengths
    4 waiting-time values
    4 CO2 emission values
    1 current-green indicator
    """

    metadata = {
        "render_modes": [],
    }

    def __init__(self) -> None:
        super().__init__()

        self.action_space = spaces.Discrete(2)

        self.observation_space = spaces.Box(
            low=0.0,
            high=np.inf,
            shape=(13,),
            dtype=np.float32,
        )

        self.current_action = 0
        self.running = False
        self.episode_reward = 0.0

    def _start_sumo(self) -> None:
        if self.running:
            traci.close()
            self.running = False

        traci.start(
            [
                "sumo",
                "-c",
                str(SUMO_CONFIG),
            ]
        )

        self.running = True

    def _advance(
        self,
        steps: int,
    ) -> None:
        for _ in range(steps):
            if (
                traci.simulation.getMinExpectedNumber()
                <= 0
            ):
                break

            traci.simulationStep()

    def _set_green(
        self,
        action: int,
    ) -> None:
        """
        Explicitly force the requested green phase.

        This prevents SUMO's original fixed-time controller
        from automatically changing the phase while the RL
        controller is active.
        """

        if action == 0:
            phase = GREEN_EW
        elif action == 1:
            phase = GREEN_NS
        else:
            raise ValueError(
                f"Invalid action: {action}"
            )

        traci.trafficlight.setPhase(
            TLS_ID,
            phase,
        )

        # Give SUMO a long remaining phase duration.
        # EcoTwin itself decides when switching occurs.
        traci.trafficlight.setPhaseDuration(
            TLS_ID,
            1000,
        )

    def _apply_action(
        self,
        action: int,
    ) -> None:
        """
        Apply one RL action for exactly DECISION_INTERVAL
        simulation seconds.

        If the requested direction changes:

            3 s yellow
            +
            12 s requested green

        If it remains unchanged:

            15 s requested green
        """

        switching = (
            action != self.current_action
        )

        if switching:
            if (
                self.current_action == 0
                and action == 1
            ):
                yellow_phase = (
                    YELLOW_EW_TO_NS
                )

            elif (
                self.current_action == 1
                and action == 0
            ):
                yellow_phase = (
                    YELLOW_NS_TO_EW
                )

            else:
                raise ValueError(
                    "Invalid traffic-light transition."
                )

            traci.trafficlight.setPhase(
                TLS_ID,
                yellow_phase,
            )

            traci.trafficlight.setPhaseDuration(
                TLS_ID,
                YELLOW_DURATION,
            )

            self._advance(
                YELLOW_DURATION
            )

            self._set_green(
                action
            )

            green_steps = (
                DECISION_INTERVAL
                - YELLOW_DURATION
            )

            self._advance(
                green_steps
            )

        else:
            # Reassert the desired phase so the original
            # SUMO timing program cannot take control.
            self._set_green(
                action
            )

            self._advance(
                DECISION_INTERVAL
            )

        self.current_action = action

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict | None = None,
    ):
        super().reset(seed=seed)

        self._start_sumo()

        self.current_action = 0
        self.episode_reward = 0.0

        self._set_green(
            self.current_action
        )

        # Produce an initial observable state.
        traci.simulationStep()

        state = (
            collect_intersection_state()
        )

        observation = (
            state.as_array()
        )

        info = {
            "simulation_time": (
                traci.simulation.getTime()
            ),
            "current_action": (
                self.current_action
            ),
        }

        return observation, info

    def step(
        self,
        action: int,
    ):
        action = int(action)

        if not self.action_space.contains(
            action
        ):
            raise ValueError(
                f"Action {action} is outside "
                f"{self.action_space}"
            )

        self._apply_action(
            action
        )

        state = (
            collect_intersection_state()
        )

        reward_data = (
            calculate_reward(state)
        )

        reward = float(
            reward_data.reward
        )

        self.episode_reward += reward

        terminated = (
            traci.simulation.getMinExpectedNumber()
            <= 0
        )

        truncated = False

        observation = (
            state.as_array()
        )

        info = {
            "simulation_time": (
                traci.simulation.getTime()
            ),
            "current_action": (
                self.current_action
            ),
            "queue_penalty": (
                reward_data.queue_penalty
            ),
            "waiting_penalty": (
                reward_data.waiting_penalty
            ),
            "co2_penalty": (
                reward_data.co2_penalty
            ),
            "episode_reward": (
                self.episode_reward
            ),
        }

        return (
            observation,
            reward,
            terminated,
            truncated,
            info,
        )

    def close(self) -> None:
        if self.running:
            traci.close()
            self.running = False