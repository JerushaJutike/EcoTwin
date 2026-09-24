from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

import numpy as np
import traci
from stable_baselines3 import PPO

from rl.env.state import collect_intersection_state


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SUMO_CONFIG = (
    PROJECT_ROOT
    / "simulation"
    / "config"
    / "ecotwin.sumocfg"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "rl"
    / "models"
    / "ppo_b1_initial.zip"
)


TLS_ID = "B1"

GREEN_EW = 0
YELLOW_EW_TO_NS = 1

GREEN_NS = 2
YELLOW_NS_TO_EW = 3

YELLOW_DURATION = 3
DECISION_INTERVAL = 15


class SimulationService:
    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        self._controller = "ppo"

        self._state: dict[str, Any] = {
            "running": False,
            "simulation_time": 0.0,
            "active_vehicles": 0,
            "departed_vehicles": 0,
            "arrived_vehicles": 0,
            "controller": self._controller,
            "current_action": 0,
            "decision_count": 0,
            "action_0_count": 0,
            "action_1_count": 0,
            "status": "stopped",
            "error": None,
        }

    def get_status(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._state)

    def set_controller(
        self,
        controller: str,
    ) -> None:
        if controller not in {
            "ppo",
            "fixed_time",
        }:
            raise ValueError(
                "Controller must be "
                "'ppo' or 'fixed_time'."
            )

        if (
            self._thread is not None
            and self._thread.is_alive()
        ):
            raise RuntimeError(
                "Cannot change controller "
                "while simulation is running."
            )

        self._controller = controller

        self._update_state(
            controller=controller,
        )

    def start(self) -> bool:
        if (
            self._thread is not None
            and self._thread.is_alive()
        ):
            return False

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        self._thread.start()

        return True

    def stop(self) -> bool:
        if (
            self._thread is None
            or not self._thread.is_alive()
        ):
            return False

        self._stop_event.set()

        return True

    def _update_state(
        self,
        **values: Any,
    ) -> None:
        with self._lock:
            self._state.update(values)

    def _set_green(
        self,
        action: int,
    ) -> None:
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

        traci.trafficlight.setPhaseDuration(
            TLS_ID,
            1000,
        )

    def _advance(
        self,
        steps: int,
        departed_total: int,
        arrived_total: int,
    ) -> tuple[int, int]:
        for _ in range(steps):
            if (
                traci.simulation.getMinExpectedNumber()
                <= 0
                or self._stop_event.is_set()
            ):
                break

            traci.simulationStep()

            departed_total += len(
                traci.simulation.getDepartedIDList()
            )

            arrived_total += len(
                traci.simulation.getArrivedIDList()
            )

            active_vehicles = len(
                traci.vehicle.getIDList()
            )

            simulation_time = (
                traci.simulation.getTime()
            )

            self._update_state(
                simulation_time=simulation_time,
                active_vehicles=active_vehicles,
                departed_vehicles=departed_total,
                arrived_vehicles=arrived_total,
            )

            # Slow down execution so the API/frontend
            # can observe the simulation progressing.
            time.sleep(0.05)

        return (
            departed_total,
            arrived_total,
        )

    def _apply_ppo_action(
        self,
        current_action: int,
        new_action: int,
        departed_total: int,
        arrived_total: int,
    ) -> tuple[int, int, int]:
        """
        Apply one PPO decision.

        Action 0:
            East/West green.

        Action 1:
            North/South green.

        When switching direction, apply the appropriate
        yellow phase before activating the new green.
        """

        if new_action == current_action:
            self._set_green(
                new_action
            )

            (
                departed_total,
                arrived_total,
            ) = self._advance(
                DECISION_INTERVAL,
                departed_total,
                arrived_total,
            )

            return (
                new_action,
                departed_total,
                arrived_total,
            )

        if (
            current_action == 0
            and new_action == 1
        ):
            yellow_phase = (
                YELLOW_EW_TO_NS
            )

        elif (
            current_action == 1
            and new_action == 0
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

        (
            departed_total,
            arrived_total,
        ) = self._advance(
            YELLOW_DURATION,
            departed_total,
            arrived_total,
        )

        if (
            traci.simulation.getMinExpectedNumber()
            <= 0
            or self._stop_event.is_set()
        ):
            return (
                new_action,
                departed_total,
                arrived_total,
            )

        self._set_green(
            new_action
        )

        (
            departed_total,
            arrived_total,
        ) = self._advance(
            DECISION_INTERVAL
            - YELLOW_DURATION,
            departed_total,
            arrived_total,
        )

        return (
            new_action,
            departed_total,
            arrived_total,
        )

    def _run(self) -> None:
        self._update_state(
            running=True,
            status="starting",
            simulation_time=0.0,
            active_vehicles=0,
            departed_vehicles=0,
            arrived_vehicles=0,
            current_action=0,
            decision_count=0,
            action_0_count=0,
            action_1_count=0,
            controller=self._controller,
            error=None,
        )

        departed_total = 0
        arrived_total = 0

        try:
            traci.start(
                [
                    "sumo",
                    "-c",
                    str(SUMO_CONFIG),
                ]
            )

            self._update_state(
                status="running",
            )

            if self._controller == "ppo":
                self._run_ppo_controller(
                    departed_total,
                    arrived_total,
                )

            else:
                self._run_fixed_time_controller(
                    departed_total,
                    arrived_total,
                )

            final_status = (
                "stopped"
                if self._stop_event.is_set()
                else "completed"
            )

            self._update_state(
                status=final_status,
            )

        except Exception as error:
            self._update_state(
                status="error",
                error=str(error),
            )

        finally:
            try:
                traci.close()
            except Exception:
                pass

            self._update_state(
                running=False,
            )

    def _run_ppo_controller(
        self,
        departed_total: int,
        arrived_total: int,
    ) -> None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"PPO model not found: "
                f"{MODEL_PATH}"
            )

        model = PPO.load(
            str(MODEL_PATH)
        )

        current_action = 0

        self._set_green(
            current_action
        )

        decision_count = 0

        action_counts = {
            0: 0,
            1: 0,
        }

        while (
            traci.simulation.getMinExpectedNumber()
            > 0
            and not self._stop_event.is_set()
        ):
            state = (
                collect_intersection_state()
            )

            observation = (
                state.as_normalized_array()
            )

            action, _ = model.predict(
                observation,
                deterministic=True,
            )

            action = int(
                np.asarray(action).item()
            )

            decision_count += 1
            action_counts[action] += 1

            (
                current_action,
                departed_total,
                arrived_total,
            ) = self._apply_ppo_action(
                current_action,
                action,
                departed_total,
                arrived_total,
            )

            self._update_state(
                current_action=current_action,
                decision_count=decision_count,
                action_0_count=action_counts[0],
                action_1_count=action_counts[1],
            )

    def _run_fixed_time_controller(
        self,
        departed_total: int,
        arrived_total: int,
    ) -> None:
        while (
            traci.simulation.getMinExpectedNumber()
            > 0
            and not self._stop_event.is_set()
        ):
            (
                departed_total,
                arrived_total,
            ) = self._advance(
                1,
                departed_total,
                arrived_total,
            )


simulation_service = SimulationService()