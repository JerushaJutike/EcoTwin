from pathlib import Path

import traci


# F:\Projects\EcoTwin
PROJECT_ROOT = Path(__file__).resolve().parents[2]

SUMO_CONFIG = (
    PROJECT_ROOT
    / "simulation"
    / "config"
    / "ecotwin.sumocfg"
)


def main() -> None:
    if not SUMO_CONFIG.exists():
        raise FileNotFoundError(
            f"SUMO config not found: {SUMO_CONFIG}"
        )

    sumo_command = [
        "sumo",
        "-c",
        str(SUMO_CONFIG),
    ]

    print("=" * 60)
    print("EcoTwin TraCI Test")
    print("=" * 60)
    print(f"SUMO config: {SUMO_CONFIG}")
    print("Starting SUMO...")

    traci.start(sumo_command)

    step = 0

    try:
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            step += 1

            vehicle_ids = list(traci.vehicle.getIDList())

            if step % 50 == 0:
                print(
                    f"\nStep: {step} | "
                    f"Active vehicles: {len(vehicle_ids)}"
                )

                for vehicle_id in vehicle_ids[:5]:
                    x, y = traci.vehicle.getPosition(vehicle_id)

                    speed = traci.vehicle.getSpeed(vehicle_id)

                    waiting_time = (
                        traci.vehicle.getWaitingTime(vehicle_id)
                    )

                    co2 = (
                        traci.vehicle.getCO2Emission(vehicle_id)
                    )

                    print(
                        f"  Vehicle: {vehicle_id:<10} "
                        f"| Position: ({x:7.1f}, {y:7.1f}) "
                        f"| Speed: {speed:6.2f} m/s "
                        f"| Wait: {waiting_time:6.2f} s "
                        f"| CO2: {co2:8.2f} mg/s"
                    )

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")

    finally:
        traci.close()

    print("\n" + "=" * 60)
    print("TraCI test completed.")
    print(f"Total simulation steps: {step}")
    print("=" * 60)


if __name__ == "__main__":
    main()