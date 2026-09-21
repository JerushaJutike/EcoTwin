from pathlib import Path
import sys

import numpy as np
import traci


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


from rl.env.state import collect_intersection_state


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

            if step % 40 != 0:
                continue

            state = collect_intersection_state()

            raw = state.as_array()
            normalized = state.as_normalized_array()

            print("\n" + "=" * 70)
            print(f"Step: {step}")

            print("\nRaw:")
            print(raw)

            print("\nNormalized:")
            print(normalized)

            print(
                f"\nRange: "
                f"{normalized.min():.4f} "
                f"to "
                f"{normalized.max():.4f}"
            )

            assert normalized.shape == (13,)
            assert np.all(normalized >= 0.0)
            assert np.all(normalized <= 1.0)

    finally:
        traci.close()


if __name__ == "__main__":
    main()