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

# Observation normalization constants
QUEUE_NORMALIZER = 20.0
WAIT_NORMALIZER = 400.0
CO2_NORMALIZER = 60000.0


@dataclass
class IntersectionState:
    queues: np.ndarray
    waiting_times: np.ndarray
    co2_emissions: np.ndarray
    current_green: int

    def as_array(self) -> np.ndarray:
        """
        Return the raw RL observation.

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
                    [float(self.current_green)],
                    dtype=np.float32,
                ),
            ]
        ).astype(np.float32)

    def as_normalized_array(self) -> np.ndarray:
        """
        Return a normalized observation in the range [0, 1].
        """

        normalized_queues = np.clip(
            self.queues / QUEUE_NORMALIZER,
            0.0,
            1.0,
        )

        normalized_waiting = np.clip(
            self.waiting_times / WAIT_NORMALIZER,
            0.0,
            1.0,
        )

        normalized_co2 = np.clip(
            self.co2_emissions / CO2_NORMALIZER,
            0.0,
            1.0,
        )

        return np.concatenate(
            [
                normalized_queues,
                normalized_waiting,
                normalized_co2,
                np.array(
                    [float(self.current_green)],
                    dtype=np.float32,
                ),
            ]
        ).astype(np.float32)


def get_lane_queue(lane_id: str) -> float:
    """
    Return the number of halted vehicles on a lane.
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
    Return current lane CO2 emission rate in mg/s.
    """
    return float(
        traci.lane.getCO2Emission(lane_id)
    )


def get_current_green() -> int:
    """
    Encode B1's current signal direction.

    0 = East/West green
    1 = North/South green
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
    """
    Collect the current traffic state around B1.
    """

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