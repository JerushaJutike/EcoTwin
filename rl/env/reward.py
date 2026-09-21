from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from rl.env.state import IntersectionState


# Initial normalization constants.
#
# These are engineering scale factors rather than claims
# about physical maximum values. They keep reward components
# roughly comparable for early experiments.
QUEUE_SCALE = 20.0
WAIT_SCALE = 400.0
CO2_SCALE = 60000.0


# Multi-objective reward weights.
QUEUE_WEIGHT = 0.30
WAIT_WEIGHT = 0.35
CO2_WEIGHT = 0.35


@dataclass
class RewardBreakdown:
    reward: float
    queue_penalty: float
    waiting_penalty: float
    co2_penalty: float

    def __str__(self) -> str:
        return (
            f"reward={self.reward:.4f} | "
            f"queue={self.queue_penalty:.4f} | "
            f"waiting={self.waiting_penalty:.4f} | "
            f"co2={self.co2_penalty:.4f}"
        )


def calculate_reward(
    state: IntersectionState,
) -> RewardBreakdown:
    """
    Compute EcoTwin's multi-objective reward.

    The agent receives a negative penalty for:

    - queued vehicles,
    - accumulated waiting time,
    - current CO2 emission rate.

    A reward closer to zero represents a better traffic state.
    """

    total_queue = float(
        np.sum(state.queues)
    )

    total_waiting = float(
        np.sum(state.waiting_times)
    )

    total_co2 = float(
        np.sum(state.co2_emissions)
    )

    normalized_queue = min(
        total_queue / QUEUE_SCALE,
        1.0,
    )

    normalized_waiting = min(
        total_waiting / WAIT_SCALE,
        1.0,
    )

    normalized_co2 = min(
        total_co2 / CO2_SCALE,
        1.0,
    )

    queue_penalty = (
        QUEUE_WEIGHT * normalized_queue
    )

    waiting_penalty = (
        WAIT_WEIGHT * normalized_waiting
    )

    co2_penalty = (
        CO2_WEIGHT * normalized_co2
    )

    reward = -(
        queue_penalty
        + waiting_penalty
        + co2_penalty
    )

    return RewardBreakdown(
        reward=reward,
        queue_penalty=queue_penalty,
        waiting_penalty=waiting_penalty,
        co2_penalty=co2_penalty,
    )