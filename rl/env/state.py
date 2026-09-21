from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import traci


TLS_ID = "B1"

# B1 incoming lanes
LANES = {
    "north": "A1B1_0",
    "east": "B2B1_0",
    "south": "C1B1_0",
    "west": "B0B1_0",
}

DIRECTIONS = (
    "north",
    "east",
    "south",
    "west",
)


@dataclass
class IntersectionState:
    queues: np.ndarray
    waiting_times: np.ndarray
    co2_emissions: np.ndarray
    current_green: int

    def as_array(self) -> np.ndarray:
        """
        Convert the structured state into a flat RL observation.

        Layout:
        [
            queue_N, queue_E, queue_S, queue_W,
            wait_N,  wait_E,  wait_S,  wait_W,
            co2_N,   co2_E,   co2_S,   co2_W,
            current_green
        ]
        """
        return np.concatenate(
            [
                self.queues,
                self.waiting_times,
                self.co2_emissions,
                np.array(
                    [self.current_green],
                    dtype=np.float32,
                ),
            ]
        ).astype(np.float32)


def get_lane_queue(lane_id: str) -> float:
    """
    Number of halted vehicles on a lane during the current step.
    """
    return float(
        traci.lane.getLastStepHaltingNumber(lane_id)
    )


def get_lane_waiting_time(lane_id: str) -> float:
    """
    Sum the current waiting time of vehicles present on a lane.
    """
    total_wait = 0.0

    vehicle_ids = traci.lane.getLastStepVehicleIDs(
        lane_id
    )

    for vehicle_id in vehicle_ids:
        total_wait += traci.vehicle.getWaitingTime(
            vehicle_id
        )

    return total_wait


def get_lane_co2(lane_id: str) -> float:
    """
    Return current CO2 emission rate for the lane in mg/s.
    """
    return float(
        traci.lane.getCO2Emission(lane_id)
    )


def get_current_green() -> int:
    """
    Encode B1's current traffic-light state.

    0 = East/West green
    1 = North/South green

    Yellow transition phases retain the direction they
    are transitioning away from.
    """
    phase = traci.trafficlight.getPhase(TLS_ID)

    if phase in (0, 1):
        return 0

    if phase in (2, 3):
        return 1

    raise ValueError(
        f"Unexpected traffic-light phase for {TLS_ID}: {phase}"
    )


def collect_intersection_state() -> IntersectionState:
    queues = []
    waiting_times = []
    co2_emissions = []

    for direction in DIRECTIONS:
        lane_id = LANES[direction]

        queues.append(
            get_lane_queue(lane_id)
        )

        waiting_times.append(
            get_lane_waiting_time(lane_id)
        )

        co2_emissions.append(
            get_lane_co2(lane_id)
        )

    return IntersectionState(
        queues=np.array(
            queues,
            dtype=np.float32,
        ),
        waiting_times=np.array(
            waiting_times,
            dtype=np.float32,
        ),
        co2_emissions=np.array(
            co2_emissions,
            dtype=np.float32,
        ),
        current_green=get_current_green(),
    )