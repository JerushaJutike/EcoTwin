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

        controlled_lanes = list(
            traci.trafficlight.getControlledLanes(TLS_ID)
        )

        controlled_links = (
            traci.trafficlight.getControlledLinks(TLS_ID)
        )

        print("\n" + "=" * 70)
        print(f"EcoTwin Controlled Lanes — Traffic Light {TLS_ID}")
        print("=" * 70)

        unique_lanes = list(dict.fromkeys(controlled_lanes))

        print("\nControlled lanes:")

        for lane_id in unique_lanes:
            edge_id = traci.lane.getEdgeID(lane_id)
            lane_length = traci.lane.getLength(lane_id)
            max_speed = traci.lane.getMaxSpeed(lane_id)

            print(
                f"  Lane={lane_id:<15} "
                f"Edge={edge_id:<10} "
                f"Length={lane_length:7.2f} m "
                f"MaxSpeed={max_speed:5.2f} m/s"
            )

        print(
            f"\nUnique controlled lanes: "
            f"{len(unique_lanes)}"
        )

        print("\nControlled links:")

        for signal_index, links in enumerate(controlled_links):
            print(f"\nSignal index {signal_index}:")

            for link in links:
                incoming_lane = link[0]
                outgoing_lane = link[1]
                via_lane = link[2]

                print(
                    f"  {incoming_lane} "
                    f"-> {outgoing_lane} "
                    f"(via {via_lane})"
                )

    finally:
        traci.close()


if __name__ == "__main__":
    main()