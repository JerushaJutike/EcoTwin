import json
from pathlib import Path

from simulation.rl.environment.ecotwin_env import EcoTwinEnv
from simulation.rl.agents.rl_controller import RLController


class RLEvaluation:
    """
    Evaluate the trained Q-learning controller
    for the same 200 SUMO seconds used by
    the fixed-time baseline.
    """

    def __init__(
        self,
        simulation_steps=200,
        decision_interval=10,
    ):
        self.simulation_steps = simulation_steps
        self.decision_interval = decision_interval

        self.decision_count = (
            simulation_steps // decision_interval
        )

    def run(self):
        """Run the trained RL controller and collect metrics."""

        env = EcoTwinEnv()
        controller = RLController()

        total_waiting_time = 0.0
        total_co2 = 0.0
        total_speed = 0.0
        speed_samples = 0

        try:
            state = env.reset()
            rl_state = state["rl_state"]

            for decision_number in range(
                self.decision_count
            ):

                action = controller.choose_action(
                    rl_state
                )

                next_state, reward = env.step(
                    action
                )

                vehicle_count = next_state[
                    "vehicle_count"
                ]

                average_speed = next_state[
                    "average_speed"
                ]

                waiting_time = next_state[
                    "waiting_time"
                ]

                co2 = next_state[
                    "co2"
                ]

                total_waiting_time += waiting_time
                total_co2 += co2

                if vehicle_count > 0:
                    total_speed += (
                        average_speed
                        * vehicle_count
                    )

                    speed_samples += (
                        vehicle_count
                    )

                rl_state = next_state[
                    "rl_state"
                ]

                if (
                    (decision_number + 1)
                    % 5
                    == 0
                ):
                    simulation_time = (
                        (decision_number + 1)
                        * self.decision_interval
                    )

                    print(
                        f"Simulation time: "
                        f"{simulation_time}/"
                        f"{self.simulation_steps} seconds"
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