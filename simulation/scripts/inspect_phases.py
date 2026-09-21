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


def main() -> None:
    traci.start(
        [
            "sumo",
            "-c",
            str(SUMO_CONFIG),
        ]
    )

    try:
        traci.simulationStep()

        programs = traci.trafficlight.getAllProgramLogics(TLS_ID)

        print(f"\nTraffic Light: {TLS_ID}")
        print("=" * 70)

        for program in programs:
            print(f"Program ID: {program.programID}")
            print(f"Current phase index: {program.currentPhaseIndex}")
            print()

            for index, phase in enumerate(program.phases):
                print(
                    f"Phase {index}: "
                    f"duration={phase.duration:.1f}s | "
                    f"state={phase.state}"
                )

    finally:
        traci.close()


if __name__ == "__main__":
    main()