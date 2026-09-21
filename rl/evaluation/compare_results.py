from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = PROJECT_ROOT / "data" / "results"

BASELINE_FILE = RESULTS_DIR / "baseline_metrics.json"
PPO_FILE = RESULTS_DIR / "ppo_metrics.json"
COMPARISON_FILE = RESULTS_DIR / "comparison_metrics.json"


def percent_change(
    baseline: float,
    new_value: float,
) -> float:
    if baseline == 0:
        return 0.0

    return (
        (new_value - baseline)
        / baseline
        * 100.0
    )


def percent_reduction(
    baseline: float,
    new_value: float,
) -> float:
    if baseline == 0:
        return 0.0

    return (
        (baseline - new_value)
        / baseline
        * 100.0
    )


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing results file: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main() -> None:
    baseline = load_json(
        BASELINE_FILE
    )

    ppo = load_json(
        PPO_FILE
    )

    waiting_reduction = percent_reduction(
        baseline[
            "average_waiting_time_seconds"
        ],
        ppo[
            "average_waiting_time_seconds"
        ],
    )

    co2_reduction = percent_reduction(
        baseline[
            "total_co2_g"
        ],
        ppo[
            "total_co2_g"
        ],
    )

    speed_change = percent_change(
        baseline[
            "average_speed_kmh"
        ],
        ppo[
            "average_speed_kmh"
        ],
    )

    duration_reduction = percent_reduction(
        baseline[
            "simulation_time_seconds"
        ],
        ppo[
            "simulation_time_seconds"
        ],
    )

    comparison = {
        "baseline": {
            "average_waiting_time_seconds": (
                baseline[
                    "average_waiting_time_seconds"
                ]
            ),
            "total_co2_g": (
                baseline[
                    "total_co2_g"
                ]
            ),
            "average_speed_kmh": (
                baseline[
                    "average_speed_kmh"
                ]
            ),
            "completed_trips": (
                baseline[
                    "completed_trips"
                ]
            ),
            "simulation_time_seconds": (
                baseline[
                    "simulation_time_seconds"
                ]
            ),
        },
        "ppo": {
            "average_waiting_time_seconds": (
                ppo[
                    "average_waiting_time_seconds"
                ]
            ),
            "total_co2_g": (
                ppo[
                    "total_co2_g"
                ]
            ),
            "average_speed_kmh": (
                ppo[
                    "average_speed_kmh"
                ]
            ),
            "completed_trips": (
                ppo[
                    "completed_trips"
                ]
            ),
            "simulation_time_seconds": (
                ppo[
                    "simulation_time_seconds"
                ]
            ),
        },
        "improvements": {
            "waiting_time_reduction_percent": round(
                waiting_reduction,
                3,
            ),
            "co2_reduction_percent": round(
                co2_reduction,
                3,
            ),
            "average_speed_change_percent": round(
                speed_change,
                3,
            ),
            "simulation_duration_reduction_percent": round(
                duration_reduction,
                3,
            ),
        },
    }

    with COMPARISON_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            comparison,
            file,
            indent=4,
        )

    print("=" * 70)
    print("EcoTwin Baseline vs PPO Comparison")
    print("=" * 70)

    print(
        f"Average waiting time:\n"
        f"  Baseline : "
        f"{baseline['average_waiting_time_seconds']:.3f} s\n"
        f"  PPO      : "
        f"{ppo['average_waiting_time_seconds']:.3f} s\n"
        f"  Reduction: "
        f"{waiting_reduction:.2f}%"
    )

    print()

    print(
        f"Total CO2:\n"
        f"  Baseline : "
        f"{baseline['total_co2_g']:.3f} g\n"
        f"  PPO      : "
        f"{ppo['total_co2_g']:.3f} g\n"
        f"  Reduction: "
        f"{co2_reduction:.2f}%"
    )

    print()

    print(
        f"Average speed:\n"
        f"  Baseline : "
        f"{baseline['average_speed_kmh']:.3f} km/h\n"
        f"  PPO      : "
        f"{ppo['average_speed_kmh']:.3f} km/h\n"
        f"  Change   : "
        f"{speed_change:+.2f}%"
    )

    print()

    print(
        f"Completed trips:\n"
        f"  Baseline : "
        f"{baseline['completed_trips']}\n"
        f"  PPO      : "
        f"{ppo['completed_trips']}"
    )

    print()

    print(
        f"Simulation duration:\n"
        f"  Baseline : "
        f"{baseline['simulation_time_seconds']:.2f} s\n"
        f"  PPO      : "
        f"{ppo['simulation_time_seconds']:.2f} s\n"
        f"  Reduction: "
        f"{duration_reduction:.2f}%"
    )

    print("=" * 70)

    print(
        f"\nComparison saved to:\n"
        f"{COMPARISON_FILE}"
    )


if __name__ == "__main__":
    main()