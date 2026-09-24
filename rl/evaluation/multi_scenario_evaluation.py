from __future__ import annotations

import json
from pathlib import Path
import statistics
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

SCENARIO_DIR = (
    PROJECT_ROOT
    / "simulation"
    / "routes"
    / "scenarios"
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
    / "multi_scenario_results.json"
)


SEEDS = [
    11,
    22,
    33,
    44,
    55,
]


TLS_ID = "B1"

GREEN_EW = 0
YELLOW_EW_TO_NS = 1

GREEN_NS = 2
YELLOW_NS_TO_EW = 3

YELLOW_DURATION = 3
DECISION_INTERVAL = 15


class Metrics:
    def __init__(self) -> None:
        self.total_co2_mg = 0.0

        self.total_speed = 0.0
        self.speed_samples = 0

        self.total_waiting_time = 0.0

        self.departed = 0
        self.arrived = 0

        self.unique_vehicle_ids: set[str] = set()

        self.steps = 0

    def update(self) -> None:
        traci.simulationStep()

        self.steps += 1

        delta_t = (
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

        self.departed += len(
            departed_ids
        )

        self.arrived += len(
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

            co2_rate = (
                traci.vehicle.getCO2Emission(
                    vehicle_id
                )
            )

            waiting_time = (
                traci.vehicle.getWaitingTime(
                    vehicle_id
                )
            )

            self.total_speed += speed
            self.speed_samples += 1

            self.total_co2_mg += (
                co2_rate * delta_t
            )

            if waiting_time > 0:
                self.total_waiting_time += (
                    delta_t
                )

    def results(
        self,
        controller: str,
        seed: int,
    ) -> dict:
        vehicle_count = len(
            self.unique_vehicle_ids
        )

        if vehicle_count:
            average_wait = (
                self.total_waiting_time
                / vehicle_count
            )
        else:
            average_wait = 0.0

        if self.speed_samples:
            average_speed_mps = (
                self.total_speed
                / self.speed_samples
            )
        else:
            average_speed_mps = 0.0

        return {
            "controller": controller,
            "seed": seed,
            "simulation_time_seconds": round(
                traci.simulation.getTime(),
                2,
            ),
            "simulation_steps": self.steps,
            "unique_vehicles": vehicle_count,
            "departed_vehicles": self.departed,
            "completed_trips": self.arrived,
            "total_co2_g": round(
                self.total_co2_mg / 1000.0,
                3,
            ),
            "total_waiting_time_seconds": round(
                self.total_waiting_time,
                2,
            ),
            "average_waiting_time_seconds": round(
                average_wait,
                3,
            ),
            "average_speed_kmh": round(
                average_speed_mps * 3.6,
                3,
            ),
        }


def sumo_command(
    route_file: Path,
) -> list[str]:
    return [
        "sumo",
        "-c",
        str(SUMO_CONFIG),
        "--route-files",
        str(route_file),
    ]


def run_baseline(
    route_file: Path,
    seed: int,
) -> dict:
    metrics = Metrics()

    traci.start(
        sumo_command(route_file)
    )

    try:
        while (
            traci.simulation.getMinExpectedNumber()
            > 0
        ):
            metrics.update()

        result = metrics.results(
            controller="fixed_time",
            seed=seed,
        )

    finally:
        traci.close()

    return result


def set_green(
    action: int,
) -> None:
    if action == 0:
        phase = GREEN_EW

    elif action == 1:
        phase = GREEN_NS

    else:
        raise ValueError(
            f"Invalid PPO action: {action}"
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
    metrics: Metrics,
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
    metrics: Metrics,
    current_action: int,
    new_action: int,
) -> int:
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
            "Invalid signal transition."
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


def run_ppo(
    model: PPO,
    route_file: Path,
    seed: int,
) -> dict:
    metrics = Metrics()

    traci.start(
        sumo_command(route_file)
    )

    current_action = 0

    try:
        set_green(
            current_action
        )

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

            current_action = apply_action(
                metrics,
                current_action,
                action,
            )

        result = metrics.results(
            controller="ppo",
            seed=seed,
        )

    finally:
        traci.close()

    return result


def mean_std(
    results: list[dict],
    metric: str,
) -> dict:
    values = [
        float(result[metric])
        for result in results
    ]

    return {
        "mean": round(
            statistics.mean(values),
            3,
        ),
        "std": round(
            statistics.stdev(values),
            3,
        ),
    }


def reduction_percent(
    baseline: float,
    ppo: float,
) -> float:
    if baseline == 0:
        return 0.0

    return (
        (baseline - ppo)
        / baseline
        * 100.0
    )


def increase_percent(
    baseline: float,
    ppo: float,
) -> float:
    if baseline == 0:
        return 0.0

    return (
        (ppo - baseline)
        / baseline
        * 100.0
    )


def main() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"PPO model not found: "
            f"{MODEL_PATH}"
        )

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model = PPO.load(
        str(MODEL_PATH)
    )

    baseline_results = []
    ppo_results = []

    print("=" * 70)
    print("EcoTwin Multi-Scenario Evaluation")
    print("=" * 70)

    for seed in SEEDS:
        route_file = (
            SCENARIO_DIR
            / f"ecotwin_seed_{seed}.rou.xml"
        )

        if not route_file.exists():
            raise FileNotFoundError(
                f"Scenario missing: "
                f"{route_file}"
            )

        print(
            f"\n{'=' * 70}"
        )

        print(
            f"Scenario seed: {seed}"
        )

        print(
            f"{'=' * 70}"
        )

        print(
            "Running fixed-time baseline..."
        )

        baseline = run_baseline(
            route_file,
            seed,
        )

        baseline_results.append(
            baseline
        )

        print(
            f"Baseline | "
            f"wait={baseline['average_waiting_time_seconds']:.3f}s | "
            f"CO2={baseline['total_co2_g']:.3f}g | "
            f"speed={baseline['average_speed_kmh']:.3f}km/h"
        )

        print(
            "Running PPO..."
        )

        ppo = run_ppo(
            model,
            route_file,
            seed,
        )

        ppo_results.append(
            ppo
        )

        print(
            f"PPO      | "
            f"wait={ppo['average_waiting_time_seconds']:.3f}s | "
            f"CO2={ppo['total_co2_g']:.3f}g | "
            f"speed={ppo['average_speed_kmh']:.3f}km/h"
        )

    metric_names = [
        "average_waiting_time_seconds",
        "total_co2_g",
        "average_speed_kmh",
        "simulation_time_seconds",
    ]

    baseline_summary = {}
    ppo_summary = {}

    for metric in metric_names:
        baseline_summary[metric] = mean_std(
            baseline_results,
            metric,
        )

        ppo_summary[metric] = mean_std(
            ppo_results,
            metric,
        )

    baseline_wait = (
        baseline_summary[
            "average_waiting_time_seconds"
        ]["mean"]
    )

    ppo_wait = (
        ppo_summary[
            "average_waiting_time_seconds"
        ]["mean"]
    )

    baseline_co2 = (
        baseline_summary[
            "total_co2_g"
        ]["mean"]
    )

    ppo_co2 = (
        ppo_summary[
            "total_co2_g"
        ]["mean"]
    )

    baseline_speed = (
        baseline_summary[
            "average_speed_kmh"
        ]["mean"]
    )

    ppo_speed = (
        ppo_summary[
            "average_speed_kmh"
        ]["mean"]
    )

    comparison = {
        "scenario_seeds": SEEDS,
        "number_of_scenarios": len(SEEDS),
        "baseline_runs": baseline_results,
        "ppo_runs": ppo_results,
        "baseline_summary": baseline_summary,
        "ppo_summary": ppo_summary,
        "mean_improvements": {
            "waiting_time_reduction_percent": round(
                reduction_percent(
                    baseline_wait,
                    ppo_wait,
                ),
                3,
            ),
            "co2_reduction_percent": round(
                reduction_percent(
                    baseline_co2,
                    ppo_co2,
                ),
                3,
            ),
            "average_speed_increase_percent": round(
                increase_percent(
                    baseline_speed,
                    ppo_speed,
                ),
                3,
            ),
        },
    }

    with RESULT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            comparison,
            file,
            indent=4,
        )

    print("\n" + "=" * 70)
    print("MULTI-SCENARIO SUMMARY")
    print("=" * 70)

    print(
        "\nAverage waiting time:"
    )

    print(
        f"  Baseline : "
        f"{baseline_wait:.3f} "
        f"± "
        f"{baseline_summary['average_waiting_time_seconds']['std']:.3f} s"
    )

    print(
        f"  PPO      : "
        f"{ppo_wait:.3f} "
        f"± "
        f"{ppo_summary['average_waiting_time_seconds']['std']:.3f} s"
    )

    print(
        f"  Reduction: "
        f"{comparison['mean_improvements']['waiting_time_reduction_percent']:.2f}%"
    )

    print(
        "\nTotal CO2:"
    )

    print(
        f"  Baseline : "
        f"{baseline_co2:.3f} "
        f"± "
        f"{baseline_summary['total_co2_g']['std']:.3f} g"
    )

    print(
        f"  PPO      : "
        f"{ppo_co2:.3f} "
        f"± "
        f"{ppo_summary['total_co2_g']['std']:.3f} g"
    )

    print(
        f"  Reduction: "
        f"{comparison['mean_improvements']['co2_reduction_percent']:.2f}%"
    )

    print(
        "\nAverage speed:"
    )

    print(
        f"  Baseline : "
        f"{baseline_speed:.3f} "
        f"± "
        f"{baseline_summary['average_speed_kmh']['std']:.3f} km/h"
    )

    print(
        f"  PPO      : "
        f"{ppo_speed:.3f} "
        f"± "
        f"{ppo_summary['average_speed_kmh']['std']:.3f} km/h"
    )

    print(
        f"  Increase : "
        f"{comparison['mean_improvements']['average_speed_increase_percent']:.2f}%"
    )

    print(
        "\nResults saved to:"
    )

    print(
        RESULT_FILE
    )


if __name__ == "__main__":
    main()