from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import traci
from stable_baselines3 import PPO


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


from rl.env.state import collect_intersection_state


SUMO_CONFIG = (
    PROJECT_ROOT
    / "simulation"
    / "config"
    / "ecotwin.sumocfg"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "rl"
    / "models"
    / "ppo_b1_initial.zip"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "data"
    / "results"
)

RESULT_FILE = (
    RESULTS_DIR
    / "ppo_metrics.json"
)


TLS_ID = "B1"

GREEN_EW = 0
YELLOW_EW_TO_NS = 1

GREEN_NS = 2
YELLOW_NS_TO_EW = 3

YELLOW_DURATION = 3
DECISION_INTERVAL = 15


class EvaluationMetrics:
    def __init__(self) -> None:
        self.total_co2_mg = 0.0

        self.total_speed = 0.0
        self.speed_samples = 0

        self.total_waiting_time = 0.0

        self.departed_vehicles = 0
        self.arrived_vehicles = 0

        self.unique_vehicle_ids: set[str] = set()

        self.simulation_steps = 0

    def update(self) -> None:
        """
        Advance SUMO by one second and record metrics
        using the same definitions as the baseline.
        """

        traci.simulationStep()

        self.simulation_steps += 1

        step_length = (
            traci.simulation.getDeltaT()
        )

        vehicle_ids = list(
            traci.vehicle.getIDList()
        )

        departed_ids = (
            traci.simulation.getDepartedIDList()
        )

        arrived_ids = (
            traci.simulation.getArrivedIDList()
        )

        self.departed_vehicles += len(
            departed_ids
        )

        self.arrived_vehicles += len(
            arrived_ids
        )

        self.unique_vehicle_ids.update(
            vehicle_ids
        )

        self.unique_vehicle_ids.update(
            departed_ids
        )

        for vehicle_id in vehicle_ids:
            speed = (
                traci.vehicle.getSpeed(
                    vehicle_id
                )
            )

            co2_mg_per_second = (
                traci.vehicle.getCO2Emission(
                    vehicle_id
                )
            )

            waiting_time = (
                traci.vehicle.getWaitingTime(
                    vehicle_id
                )
            )

            self.total_co2_mg += (
                co2_mg_per_second
                * step_length
            )

            self.total_speed += speed
            self.speed_samples += 1

            if waiting_time > 0:
                self.total_waiting_time += (
                    step_length
                )


def set_green(action: int) -> None:
    if action == 0:
        phase = GREEN_EW

    elif action == 1:
        phase = GREEN_NS

    else:
        raise ValueError(
            f"Invalid action: {action}"
        )

    traci.trafficlight.setPhase(
        TLS_ID,
        phase,
    )

    traci.trafficlight.setPhaseDuration(
        TLS_ID,
        1000,
    )


def advance(
    metrics: EvaluationMetrics,
    steps: int,
) -> None:
    for _ in range(steps):
        if (
            traci.simulation.getMinExpectedNumber()
            <= 0
        ):
            break

        metrics.update()


def apply_action(
    metrics: EvaluationMetrics,
    current_action: int,
    new_action: int,
) -> int:
    """
    Apply an action using the same timing rules
    used during PPO training.
    """

    if new_action == current_action:
        set_green(
            new_action
        )

        advance(
            metrics,
            DECISION_INTERVAL,
        )

        return new_action

    if (
        current_action == 0
        and new_action == 1
    ):
        yellow_phase = (
            YELLOW_EW_TO_NS
        )

    elif (
        current_action == 1
        and new_action == 0
    ):
        yellow_phase = (
            YELLOW_NS_TO_EW
        )

    else:
        raise ValueError(
            "Invalid traffic-light transition."
        )

    traci.trafficlight.setPhase(
        TLS_ID,
        yellow_phase,
    )

    traci.trafficlight.setPhaseDuration(
        TLS_ID,
        YELLOW_DURATION,
    )

    advance(
        metrics,
        YELLOW_DURATION,
    )

    if (
        traci.simulation.getMinExpectedNumber()
        <= 0
    ):
        return new_action

    set_green(
        new_action
    )

    advance(
        metrics,
        DECISION_INTERVAL
        - YELLOW_DURATION,
    )

    return new_action


def main() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"PPO model not found: {MODEL_PATH}"
        )

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 70)
    print("EcoTwin PPO Evaluation")
    print("=" * 70)

    model = PPO.load(
        str(MODEL_PATH)
    )

    traci.start(
        [
            "sumo",
            "-c",
            str(SUMO_CONFIG),
        ]
    )

    metrics = EvaluationMetrics()

    current_action = 0
    decision_count = 0
    action_counts = {
        0: 0,
        1: 0,
    }

    try:
        set_green(
            current_action
        )

        # First simulation second, matching the
        # environment's reset behaviour.
        metrics.update()

        while (
            traci.simulation.getMinExpectedNumber()
            > 0
        ):
            state = (
                collect_intersection_state()
            )

            observation = (
                state.as_normalized_array()
            )

            action, _ = model.predict(
                observation,
                deterministic=True,
            )

            action = int(
                np.asarray(action).item()
            )

            decision_count += 1
            action_counts[action] += 1

            current_action = apply_action(
                metrics,
                current_action,
                action,
            )

            if decision_count % 10 == 0:
                print(
                    f"Decision={decision_count:3d} | "
                    f"Time={traci.simulation.getTime():7.1f}s | "
                    f"Action={action} | "
                    f"Running="
                    f"{len(traci.vehicle.getIDList()):3d}"
                )

        final_simulation_time = (
            traci.simulation.getTime()
        )

    finally:
        traci.close()

    unique_vehicle_count = len(
        metrics.unique_vehicle_ids
    )

    if unique_vehicle_count > 0:
        average_waiting_time = (
            metrics.total_waiting_time
            / unique_vehicle_count
        )

    else:
        average_waiting_time = 0.0

    if metrics.speed_samples > 0:
        average_speed_mps = (
            metrics.total_speed
            / metrics.speed_samples
        )

    else:
        average_speed_mps = 0.0

    average_speed_kmh = (
        average_speed_mps * 3.6
    )

    total_co2_g = (
        metrics.total_co2_mg / 1000.0
    )

    results = {
        "controller": "PPO",
        "model": MODEL_PATH.name,
        "simulation_time_seconds": round(
            final_simulation_time,
            2,
        ),
        "simulation_steps": (
            metrics.simulation_steps
        ),
        "unique_vehicles": (
            unique_vehicle_count
        ),
        "departed_vehicles": (
            metrics.departed_vehicles
        ),
        "completed_trips": (
            metrics.arrived_vehicles
        ),
        "total_co2_mg": round(
            metrics.total_co2_mg,
            2,
        ),
        "total_co2_g": round(
            total_co2_g,
            3,
        ),
        "total_waiting_time_seconds": round(
            metrics.total_waiting_time,
            2,
        ),
        "average_waiting_time_seconds": round(
            average_waiting_time,
            3,
        ),
        "average_speed_mps": round(
            average_speed_mps,
            3,
        ),
        "average_speed_kmh": round(
            average_speed_kmh,
            3,
        ),
        "ppo_decisions": (
            decision_count
        ),
        "action_0_count": (
            action_counts[0]
        ),
        "action_1_count": (
            action_counts[1]
        ),
    }

    with RESULT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=4,
        )

    print("\n" + "=" * 70)
    print("PPO EVALUATION RESULTS")
    print("=" * 70)

    print(
        f"Simulation duration : "
        f"{results['simulation_time_seconds']:.2f} s"
    )

    print(
        f"Unique vehicles     : "
        f"{results['unique_vehicles']}"
    )

    print(
        f"Departed vehicles   : "
        f"{results['departed_vehicles']}"
    )

    print(
        f"Completed trips     : "
        f"{results['completed_trips']}"
    )

    print(
        f"Total CO2           : "
        f"{results['total_co2_g']:.3f} g"
    )

    print(
        f"Total waiting time  : "
        f"{results['total_waiting_time_seconds']:.2f} s"
    )

    print(
        f"Avg waiting time    : "
        f"{results['average_waiting_time_seconds']:.3f} s/vehicle"
    )

    print(
        f"Average speed       : "
        f"{results['average_speed_kmh']:.3f} km/h"
    )

    print(
        f"PPO decisions       : "
        f"{results['ppo_decisions']}"
    )

    print(
        f"Action 0 selections : "
        f"{results['action_0_count']}"
    )

    print(
        f"Action 1 selections : "
        f"{results['action_1_count']}"
    )

    print("=" * 70)

    print(
        f"\nResults saved to:\n"
        f"{RESULT_FILE}"
    )


if __name__ == "__main__":
    main()