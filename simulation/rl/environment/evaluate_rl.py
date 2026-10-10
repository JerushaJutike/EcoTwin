import json
from pathlib import Path

import traci

from simulation.rl.environment.ecotwin_env import EcoTwinEnv
from simulation.rl.agents.rl_controller import RLController


class RLEvaluation:
    """
    Evaluate the trained Q-learning controller
    for the same number of SUMO seconds used
    by the fixed-time baseline.

    The RL controller selects a new traffic-light
    action every decision_interval seconds, while
    evaluation metrics are sampled every SUMO second.
    """

    def __init__(
        self,
        simulation_steps=200,
        decision_interval=10,
    ):
        self.simulation_steps = simulation_steps
        self.decision_interval = decision_interval

    def run(self):
        """
        Run the trained RL controller and collect
        directly comparable traffic metrics.

        Metrics:
        - CO2 is sampled for every active vehicle every SUMO second.
        - Waiting time uses each vehicle's latest accumulated waiting time.
        - Average speed is calculated across all vehicle-second samples.
        """

        env = EcoTwinEnv()
        controller = RLController()

        total_co2 = 0.0
        total_speed = 0.0
        speed_samples = 0

        # Stores the latest accumulated waiting time
        # observed for every vehicle.
        final_waiting_times = {}

        try:
            state = env.reset()
            rl_state = state["rl_state"]

            for simulation_second in range(
                self.simulation_steps
            ):
                # The RL agent makes a traffic-light
                # decision only at the configured interval.
                if (
                    simulation_second
                    % self.decision_interval
                    == 0
                ):
                    action = controller.choose_action(
                        rl_state
                    )

                    env.apply_action(
                        action
                    )

                # Advance SUMO exactly one second.
                traci.simulationStep()

                # Read the new environment state
                # after that one-second simulation step.
                state = env.get_state()

                vehicle_ids = (
                    traci.vehicle.getIDList()
                )

                for vehicle_id in vehicle_ids:
                    final_waiting_times[
                        vehicle_id
                    ] = (
                        traci.vehicle
                        .getAccumulatedWaitingTime(
                            vehicle_id
                        )
                    )

                    total_co2 += (
                        traci.vehicle.getCO2Emission(
                            vehicle_id
                        )
                    )

                    total_speed += (
                        traci.vehicle.getSpeed(
                            vehicle_id
                        )
                    )

                    speed_samples += 1

                rl_state = state["rl_state"]

                if (
                    (simulation_second + 1)
                    % 50
                    == 0
                ):
                    print(
                        f"Simulation time: "
                        f"{simulation_second + 1}/"
                        f"{self.simulation_steps} seconds"
                    )

            total_waiting_time = sum(
                final_waiting_times.values()
            )

            if speed_samples > 0:
                overall_average_speed = (
                    total_speed
                    / speed_samples
                )
            else:
                overall_average_speed = 0.0

            return {
                "simulation_steps":
                    self.simulation_steps,

                "total_waiting_time":
                    total_waiting_time,

                "total_co2":
                    total_co2,

                "average_speed":
                    overall_average_speed,
            }

        finally:
            env.close()

    def save_results(
        self,
        results,
        output_path="data/results/rl_results.json",
    ):
        """Save RL evaluation results to JSON."""

        output_file = Path(
            output_path
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                results,
                file,
                indent=4,
            )


def main():
    print(
        "Starting EcoTwin RL evaluation..."
    )

    evaluation = RLEvaluation(
        simulation_steps=200,
        decision_interval=10,
    )

    try:
        results = evaluation.run()

        print(
            "\nRL Evaluation Results"
        )

        print(
            "---------------------"
        )

        print(
            "Simulation steps:",
            results[
                "simulation_steps"
            ],
        )

        print(
            "Total waiting time:",
            results[
                "total_waiting_time"
            ],
        )

        print(
            "Total CO2:",
            results[
                "total_co2"
            ],
        )

        print(
            "Average speed:",
            results[
                "average_speed"
            ],
        )

        evaluation.save_results(
            results
        )

        print(
            "\nRL results saved successfully."
        )

    except Exception as error:
        print(
            "\nRL evaluation failed."
        )

        print(
            f"Error: {error}"
        )


if __name__ == "__main__":
    main()