from pathlib import Path

import traci


PROJECT_ROOT = Path(__file__).resolve().parents[2]

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
        # Advance once so SUMO is initialized.
        traci.simulationStep()

        traffic_lights = list(
            traci.trafficlight.getIDList()
        )

        print("\nEcoTwin Traffic Lights")
        print("=" * 60)

        if not traffic_lights:
            print("No traffic lights were found.")
            return

        for tls_id in traffic_lights:
            phase = traci.trafficlight.getPhase(tls_id)
            state = traci.trafficlight.getRedYellowGreenState(
                tls_id
            )

            print(f"Traffic light: {tls_id}")
            print(f"  Current phase: {phase}")
            print(f"  Signal state : {state}")
            print()

        print(f"Total traffic lights: {len(traffic_lights)}")

    finally:
        traci.close()


if __name__ == "__main__":
    main()