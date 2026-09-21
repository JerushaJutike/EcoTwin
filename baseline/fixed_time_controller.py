import traci


class FixedTimeController:
    """
    Fixed-time traffic-light baseline controller.

    This controller keeps the existing SUMO traffic-light
    timing unchanged and collects basic traffic metrics.
    """

    def __init__(
        self,
        sumo_config="simulation/sumo/config/grid.sumocfg",
        simulation_steps=200,
    ):
        self.sumo_config = sumo_config
        self.simulation_steps = simulation_steps

    def start(self):
        """Start the SUMO simulation through TraCI."""

        traci.start(
            [
                "sumo",
                "-c",
                self.sumo_config,
            ]
        )

    def run(self):
        """
        Run SUMO using its existing fixed-time
        traffic-light program.
        """

        total_waiting_time = 0.0
        total_co2 = 0.0
        total_speed = 0.0
        speed_samples = 0

        for _ in range(self.simulation_steps):
            traci.simulationStep()

            vehicle_ids = traci.vehicle.getIDList()

            for vehicle_id in vehicle_ids:
                total_waiting_time += (
                    traci.vehicle.getAccumulatedWaitingTime(
                        vehicle_id
                    )
                )

                total_co2 += (
                    traci.vehicle.getCO2Emission(
                        vehicle_id
                    )
                )

                total_speed += (
                    traci.vehicle.getSpeed(
                        vehicle_id
                    )
                )

                speed_samples += 1

        average_speed = (
            total_speed / speed_samples
            if speed_samples > 0
            else 0.0
        )

        return {
            "total_waiting_time": total_waiting_time,
            "total_co2": total_co2,
            "average_speed": average_speed,
        }

    def close(self):
        """Close the SUMO/TraCI connection."""

        traci.close()


if __name__ == "__main__":
    controller = FixedTimeController()

    try:
        controller.start()

        results = controller.run()

        print("\nFixed-Time Baseline Results")
        print("---------------------------")
        print(
            "Total waiting time:",
            results["total_waiting_time"],
        )
        print(
            "Total CO2:",
            results["total_co2"],
        )
        print(
            "Average speed:",
            results["average_speed"],
        )

    finally:
        controller.close()