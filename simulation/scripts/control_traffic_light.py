from pathlib import Path

import traci


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SUMO_CONFIG = (
    PROJECT_ROOT
    / "simulation"
    / "config"
    / "ecotwin.sumocfg"
)

TLS_ID = "B1"

# Actual phases discovered from our SUMO network.
GREEN_PHASE_A = 0
YELLOW_A_TO_B = 1
GREEN_PHASE_B = 2
YELLOW_B_TO_A = 3

GREEN_DURATION = 20
YELLOW_DURATION = 3


def set_phase(phase: int, duration: int) -> None:
    """Set B1 to a specific SUMO traffic-light phase."""
    traci.trafficlight.setPhase(TLS_ID, phase)
    traci.trafficlight.setPhaseDuration(TLS_ID, duration)


def main() -> None:
    sumo_command = [
        "sumo-gui",
        "-c",
        str(SUMO_CONFIG),
        "--start",
    ]

    print("=" * 60)
    print("EcoTwin Traffic Light Control Test")
    print("=" * 60)

    traci.start(sumo_command)

    try:
        step = 0

        # Start explicitly with green phase A.
        set_phase(GREEN_PHASE_A, GREEN_DURATION)

        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            step += 1

            # A -> B transition
            if step == 20:
                print("\nSwitching A -> Yellow")
                set_phase(YELLOW_A_TO_B, YELLOW_DURATION)

            elif step == 23:
                print("Switching Yellow -> B")
                set_phase(GREEN_PHASE_B, GREEN_DURATION)

            # B -> A transition
            elif step == 43:
                print("\nSwitching B -> Yellow")
                set_phase(YELLOW_B_TO_A, YELLOW_DURATION)

            elif step == 46:
                print("Switching Yellow -> A")
                set_phase(GREEN_PHASE_A, GREEN_DURATION)

            if step % 5 == 0:
                current_phase = traci.trafficlight.getPhase(TLS_ID)

                state = (
                    traci.trafficlight
                    .getRedYellowGreenState(TLS_ID)
                )

                vehicle_count = len(
                    traci.vehicle.getIDList()
                )

                print(
                    f"Step={step:3d} | "
                    f"B1 phase={current_phase} | "
                    f"vehicles={vehicle_count:3d} | "
                    f"state={state}"
                )

            # We only need 65 seconds for this test.
            if step >= 65:
                break

    finally:
        traci.close()

    print("\nTraffic-light control test completed.")


if __name__ == "__main__":
    main()