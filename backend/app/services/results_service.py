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
            f"Comparison results not found: {RESULTS_PATH}"
        )

    with open(
        RESULTS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)