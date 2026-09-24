from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]

NETWORK_FILE = (
    PROJECT_ROOT
    / "simulation"
    / "network"
    / "ecotwin.net.xml"
)

SCENARIO_DIR = (
    PROJECT_ROOT
    / "simulation"
    / "routes"
    / "scenarios"
)

SEEDS = [
    11,
    22,
    33,
    44,
    55,
]

END_TIME = 1000
PERIOD = 2


def get_random_trips_script() -> Path:
    sumo_home = os.environ.get("SUMO_HOME")

    if not sumo_home:
        raise EnvironmentError(
            "SUMO_HOME environment variable is not set."
        )

    script = (
        Path(sumo_home)
        / "tools"
        / "randomTrips.py"
    )

    if not script.exists():
        raise FileNotFoundError(
            f"randomTrips.py not found: {script}"
        )

    return script


def generate_scenario(
    random_trips_script: Path,
    seed: int,
) -> Path:
    route_file = (
        SCENARIO_DIR
        / f"ecotwin_seed_{seed}.rou.xml"
    )

    command = [
        sys.executable,
        str(random_trips_script),
        "-n",
        str(NETWORK_FILE),
        "-r",
        str(route_file),
        "-e",
        str(END_TIME),
        "-p",
        str(PERIOD),
        "--seed",
        str(seed),
        "--validate",
    ]

    print(
        f"Generating traffic scenario "
        f"with seed {seed}..."
    )

    subprocess.run(
        command,
        check=True,
    )

    return route_file


def main() -> None:
    if not NETWORK_FILE.exists():
        raise FileNotFoundError(
            f"SUMO network not found: "
            f"{NETWORK_FILE}"
        )

    SCENARIO_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    random_trips_script = (
        get_random_trips_script()
    )

    print("=" * 70)
    print("EcoTwin Traffic Scenario Generator")
    print("=" * 70)

    generated_files = []

    for seed in SEEDS:
        route_file = generate_scenario(
            random_trips_script,
            seed,
        )

        generated_files.append(
            route_file
        )

    print("\n" + "=" * 70)
    print("SCENARIOS GENERATED")
    print("=" * 70)

    for path in generated_files:
        print(path)

    print(
        f"\nTotal scenarios: "
        f"{len(generated_files)}"
    )


if __name__ == "__main__":
    main()