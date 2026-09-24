import json
from pathlib import Path


BASELINE_PATH = Path(
    "data/results/baseline_results.json"
)

RL_PATH = Path(
    "data/results/rl_results.json"
)

COMPARISON_PATH = Path(
    "data/results/comparison_results.json"
)


def load_results(file_path):
    """Load results from a JSON file."""

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def calculate_percentage_change(
    baseline,
    rl,
):
    """Calculate percentage change from baseline to RL."""

    if baseline == 0:
        return 0.0

    return (
        (rl - baseline)
        / baseline
    ) * 100


def main():
    print(
        "Starting EcoTwin baseline vs RL comparison..."
    )

    baseline = load_results(
        BASELINE_PATH
    )

    rl = load_results(
        RL_PATH
    )

    baseline_waiting = baseline[
        "total_waiting_time"
    ]

    rl_waiting = rl[
        "total_waiting_time"
    ]

    baseline_co2 = baseline[
        "total_co2"
    ]

    rl_co2 = rl[
        "total_co2"
    ]

    baseline_speed = baseline[
        "average_speed"
    ]

    rl_speed = rl[
        "average_speed"
    ]

    comparison = {
        "simulation_steps": rl[
            "simulation_steps"
        ],

        "baseline": baseline,

        "rl": rl,

        "differences": {
            "waiting_time": (
                rl_waiting
                - baseline_waiting
            ),

            "co2": (
                rl_co2
                - baseline_co2
            ),

            "average_speed": (
                rl_speed
                - baseline_speed
            ),
        },

        "percentage_change": {
            "waiting_time": calculate_percentage_change(
                baseline_waiting,
                rl_waiting,
            ),

            "co2": calculate_percentage_change(
                baseline_co2,
                rl_co2,
            ),

            "average_speed": calculate_percentage_change(
                baseline_speed,
                rl_speed,
            ),
        },
    }

    print(
        "\nBaseline vs RL Comparison"
    )

    print(
        "-------------------------"
    )

    print(
        f"Waiting time: "
        f"{baseline_waiting:.2f} -> "
        f"{rl_waiting:.2f}"
    )

    print(
        f"CO2: "
        f"{baseline_co2:.2f} -> "
        f"{rl_co2:.2f}"
    )

    print(
        f"Average speed: "
        f"{baseline_speed:.4f} -> "
        f"{rl_speed:.4f}"
    )

    print(
        "\nPercentage Changes"
    )

    print(
        "-----------------"
    )

    print(
        f"Waiting time: "
        f"{comparison['percentage_change']['waiting_time']:.2f}%"
    )

    print(
        f"CO2: "
        f"{comparison['percentage_change']['co2']:.2f}%"
    )

    print(
        f"Average speed: "
        f"{comparison['percentage_change']['average_speed']:.2f}%"
    )

    COMPARISON_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        COMPARISON_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            comparison,
            file,
            indent=4,
        )

    print(
        "\nComparison results saved successfully."
    )

    print(
        f"Saved to: {COMPARISON_PATH}"
    )


if __name__ == "__main__":
    main()