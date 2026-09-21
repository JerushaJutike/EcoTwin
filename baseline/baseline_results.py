class BaselineResults:
    """
    Stores and formats baseline traffic-control results.
    """

    def __init__(
        self,
        total_waiting_time=0.0,
        total_co2=0.0,
        average_speed=0.0,
    ):
        self.total_waiting_time = total_waiting_time
        self.total_co2 = total_co2
        self.average_speed = average_speed

    def to_dict(self):
        """
        Return the results as a dictionary.
        """

        return {
            "total_waiting_time": self.total_waiting_time,
            "total_co2": self.total_co2,
            "average_speed": self.average_speed,
        }

    def display(self):
        """
        Display the baseline results in a readable format.
        """

        print("\nFixed-Time Baseline Results")
        print("---------------------------")
        print(
            "Total waiting time:",
            self.total_waiting_time,
        )
        print(
            "Total CO2:",
            self.total_co2,
        )
        print(
            "Average speed:",
            self.average_speed,
        )