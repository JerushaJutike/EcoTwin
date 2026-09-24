from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = (
    PROJECT_ROOT
    / "data"
    / "results"
)


RESULT_FILES = {
    "baseline": (
        RESULTS_DIR
        / "baseline_metrics.json"
    ),
    "ppo": (
        RESULTS_DIR
        / "ppo_metrics.json"
    ),
    "comparison": (
        RESULTS_DIR
        / "comparison_metrics.json"
    ),
    "multi_scenario": (
        RESULTS_DIR
        / "multi_scenario_results.json"
    ),
}


def load_json_file(
    path: Path,
) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Results file not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def get_result(
    result_type: str,
) -> dict[str, Any]:
    if result_type not in RESULT_FILES:
        raise KeyError(
            f"Unknown result type: {result_type}"
        )

    return load_json_file(
        RESULT_FILES[result_type]
    )


def get_all_results() -> dict[str, Any]:
    results = {}

    for name, path in RESULT_FILES.items():
        if path.exists():
            results[name] = load_json_file(
                path
            )

    return results