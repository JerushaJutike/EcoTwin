from pathlib import Path
import sys

import traci


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


from rl.env.reward import calculate_reward
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
        for step in range(1, 301):
            traci.simulationStep()

            if step % 20 != 0:
                continue

            state = collect_intersection_state()
            result = calculate_reward(state)

            total_queue = state.queues.sum()
            total_wait = state.waiting_times.sum()
            total_co2 = state.co2_emissions.sum()

            green = (
                "E/W"
                if state.current_green == 0
                else "N/S"
            )

            print("\n" + "=" * 70)

            print(
                f"Step={step:3d} | "
                f"Green={green}"
            )

            print(
                f"Queue={total_queue:6.0f} vehicles | "
                f"Waiting={total_wait:8.2f} s | "
                f"CO2={total_co2:10.2f} mg/s"
            )

            print(result)

    finally:
        traci.close()


if __name__ == "__main__":
    main()