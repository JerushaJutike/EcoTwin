import json
from pathlib import Path


RESULTS_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "results"
    / "comparison_results.json"
)


def load_comparison_results():
    """
    Load baseline vs RL comparison results
    for the EcoTwin dashboard.
    """

    if not RESULTS_PATH.exists():
        raise FileNotFoundError(
            f"Comparison results not found: "
            f"{RESULTS_PATH}"
        )

    try:
        with open(
            RESULTS_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(
                file
            )

    except json.JSONDecodeError as error:
        raise ValueError(
            "Comparison results file contains "
            "invalid JSON."
        ) from error

    required_fields = {
        "simulation_steps",
        "baseline",
        "rl",
        "differences",
        "percentage_change",
    }

    missing_fields = (
        required_fields
        - data.keys()
    )

    if missing_fields:
        raise ValueError(
            "Comparison results are incomplete. "
            f"Missing fields: {sorted(missing_fields)}"
        )

    return data