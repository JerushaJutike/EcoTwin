import traci

from simulation.rl.problem_definition import (
    get_state as build_rl_state,
)


class EcoTwinEnv:
    """
    Basic EcoTwin reinforcement-learning environment.

    Connects Python to SUMO through TraCI and provides:
    - traffic-light observation
    - vehicle observations
    - CO2 observations
    - RL state generation
    - traffic-light actions
    - reward calculation
    - environment reset
    """

    def __init__(self, sumo_config="simulation/sumo/config/grid.sumocfg"):
        self.sumo_config = sumo_config

        # RL action choices:
        # 0 -> J1 phase 0
        # 1 -> J1 phase 2
        self.actions = {
            0: 0,
            1: 2,
        }

        # Number of SUMO seconds between RL decisions
        self.decision_interval = 10

        # Previous state used for reward calculation
        self.previous_state = None

        # Reward weights
        self.waiting_weight = 0.6
        self.co2_weight = 0.4

        # Track whether SUMO is currently running
        self.is_running = False

    def start(self):
        """Start the SUMO simulation through TraCI."""

        if self.is_running:
            return

        traci.start([
            "sumo",
            "-c",
            self.sumo_config
        ])

        self.is_running = True

    def reset(self):
        """
        Reset the RL environment.

        A reset starts a fresh SUMO simulation and
        returns the initial RL state.
        """

        if self.is_running:
            self.close()

        self.previous_state = None

        self.start()

        state = self.get_state()

        return state

    def get_state(self):
        """
        Collect the current traffic state from SUMO.

        The returned dictionary contains the detailed
        traffic information used by EcoTwin.
        """

        vehicle_ids = traci.vehicle.getIDList()

        vehicle_count = len(vehicle_ids)

        if vehicle_count > 0:

            speeds = [
                traci.vehicle.getSpeed(vehicle_id)
                for vehicle_id in vehicle_ids
            ]

            waiting_times = [
                traci.vehicle.getAccumulatedWaitingTime(vehicle_id)
                for vehicle_id in vehicle_ids
            ]

            co2_values = [
                traci.vehicle.getCO2Emission(vehicle_id)
                for vehicle_id in vehicle_ids
            ]

            average_speed = sum(speeds) / vehicle_count
            total_waiting_time = sum(waiting_times)
            total_co2 = sum(co2_values)

        else:

            average_speed = 0.0
            total_waiting_time = 0.0
            total_co2 = 0.0

        current_phase = traci.trafficlight.getPhase("J1")

        # Build the centralized RL observation
        rl_state = build_rl_state(
            total_waiting_time,
            average_speed,
            vehicle_count,
            total_co2,
            current_phase,
        )

        return {
            "vehicle_count": vehicle_count,
            "average_speed": average_speed,
            "waiting_time": total_waiting_time,
            "co2": total_co2,
            "traffic_light_phase": current_phase,

            # Centralized RL observation
            "rl_state": rl_state,
        }

    def calculate_reward(self, state):
        """
        Calculate a normalized reward using changes
        in waiting time and CO2.

        Lower waiting time and lower CO2
        produce a better reward.
        """

        if self.previous_state is None:

            self.previous_state = state

            return 0.0

        previous_waiting = self.previous_state["waiting_time"]
        previous_co2 = self.previous_state["co2"]

        waiting_change = (
            state["waiting_time"]
            - previous_waiting
        )

        co2_change = (
            state["co2"]
            - previous_co2
        )

        waiting_score = (
            waiting_change
            / max(previous_waiting, 1.0)
        )

        co2_score = (
            co2_change
            / max(previous_co2, 1.0)
        )

        waiting_score = max(
            -1.0,
            min(1.0, waiting_score)
        )

        co2_score = max(
            -1.0,
            min(1.0, co2_score)
        )

        reward = (
            -self.waiting_weight * waiting_score
            -self.co2_weight * co2_score
        )

        self.previous_state = state

        return reward

    def apply_action(self, action):
        """
        Apply an RL action to traffic light J1.
        """

        if action not in self.actions:
            raise ValueError(
                "Action must be 0 or 1."
            )

        target_phase = self.actions[action]

        traci.trafficlight.setPhase(
            "J1",
            target_phase
        )

    def step(self, action):
        """
        Apply an action and advance SUMO
        by the decision interval.
        """

        if not self.is_running:
            raise RuntimeError(
                "Environment is not running. Call reset() or start() first."
            )

        self.apply_action(action)

        for _ in range(self.decision_interval):
            traci.simulationStep()

        state = self.get_state()

        reward = self.calculate_reward(state)

        return state, reward

    def close(self):
        """Close the SUMO/TraCI connection."""

        if self.is_running:

            traci.close()

            self.is_running = False