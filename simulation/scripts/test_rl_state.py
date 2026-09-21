from pathlib import Path
import sys

import traci


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)

from rl.env.state import (
    DIRECTIONS,
    collect_intersection_state,
)


SUMO_CONFIG = (
    PROJECT_ROOT
    / "simulation"
    / "config"
    / "ecotwin.sumocfg"
)


def main() -> None:
    traci.start(
        [
            "sumo",
            "-c",
            str(SUMO_CONFIG),
        ]
    )

    try:
        for step in range(1, 201):
            traci.simulationStep()

            if step % 20 != 0:
                continue

            state = collect_intersection_state()

            print("\n" + "=" * 70)
            print(f"Simulation step: {step}")
            print(
                f"Current green: "
                f"{'E/W' if state.current_green == 0 else 'N/S'}"
            )

            print("-" * 70)

            for index, direction in enumerate(
                DIRECTIONS
            ):
                print(
                    f"{direction.capitalize():<6} | "
                    f"Queue={state.queues[index]:5.0f} | "
                    f"Wait={state.waiting_times[index]:8.2f}s | "
                    f"CO2={state.co2_emissions[index]:10.2f} mg/s"
                )

            print(
                "\nObservation vector:"
            )

            print(
                state.as_array()
            )

            print(
                f"Observation size: "
                f"{state.as_array().shape}"
            )

    finally:
        traci.close()


if __name__ == "__main__":
    main()