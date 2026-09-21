import traci


class EcoTwinEnv:
    """
    Basic EcoTwin reinforcement-learning environment.

    Connects Python to SUMO through TraCI and provides:
    - traffic-light observation
    - vehicle observations
    - CO2 observations
    - traffic-light actions
    - normalized reward calculation
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

    def start(self):
        """Start the SUMO simulation through TraCI."""
        traci.start([
            "sumo",
            "-c",
            self.sumo_config
        ])

    def get_state(self):
        """Collect the current traffic state from SUMO."""

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

        return {
            "vehicle_count": vehicle_count,
            "average_speed": average_speed,
            "waiting_time": total_waiting_time,
            "co2": total_co2,
            "traffic_light_phase": current_phase,
        }

    def calculate_reward(self, state):
        """
        Calculate a normalized reward using changes in waiting time and CO2.

        Lower waiting time and lower CO2 produce a better reward.
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

        waiting_score = waiting_change / max(previous_waiting, 1.0)
        co2_score = co2_change / max(previous_co2, 1.0)

        waiting_score = max(-1.0, min(1.0, waiting_score))
        co2_score = max(-1.0, min(1.0, co2_score))

        reward = (
            -self.waiting_weight * waiting_score
            -self.co2_weight * co2_score
        )

        self.previous_state = state

        return reward

    def apply_action(self, action):
        """Apply an RL action to traffic light J1."""

        if action not in self.actions:
            raise ValueError("Action must be 0 or 1.")

        target_phase = self.actions[action]

        traci.trafficlight.setPhase("J1", target_phase)

    def step(self, action):
        """Apply an action and advance SUMO by the decision interval."""

        self.apply_action(action)

        for _ in range(self.decision_interval):
            traci.simulationStep()

        state = self.get_state()

        reward = self.calculate_reward(state)

        return state, reward

    def close(self):
        """Close the SUMO/TraCI connection."""
        traci.close()