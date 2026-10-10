import traci

from baseline.baseline_results import BaselineResults


class FixedTimeController:
    """
    Fixed-time traffic-light baseline controller.

    This controller keeps the existing SUMO traffic-light
    timing unchanged and collects traffic metrics using
    the same per-second sampling strategy as the RL
    evaluation.
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

        Metrics:
        - CO2 is sampled for every active vehicle every SUMO second.
        - Waiting time uses each vehicle's latest accumulated waiting time.
        - Average speed is calculated across all vehicle-second samples.
        """

        total_co2 = 0.0
        total_speed = 0.0
        speed_samples = 0

        # Stores the latest accumulated waiting time
        # observed for every vehicle.
        final_waiting_times = {}

        for simulation_second in range(self.simulation_steps):
            traci.simulationStep()

            vehicle_ids = traci.vehicle.getIDList()

            for vehicle_id in vehicle_ids:
                final_waiting_times[vehicle_id] = (
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

            if (simulation_second + 1) % 50 == 0:
                print(
                    f"Simulation time: "
                    f"{simulation_second + 1}/"
                    f"{self.simulation_steps} seconds"
                )

        total_waiting_time = sum(
            final_waiting_times.values()
        )

        if speed_samples > 0:
            average_speed = (
                total_speed / speed_samples
            )
        else:
            average_speed = 0.0

        return BaselineResults(
            total_waiting_time=total_waiting_time,
            total_co2=total_co2,
            average_speed=average_speed,
        )

    def close(self):
        """Close the SUMO/TraCI connection."""

        traci.close()


if __name__ == "__main__":
    controller = FixedTimeController()

    try:
        controller.start()

        results = controller.run()

        results.display()

        results.save()

        print(
            "\nBaseline results saved successfully."
        )

    finally:
        controller.close()
