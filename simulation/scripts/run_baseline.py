from __future__ import annotations

import json
from pathlib import Path

import traci


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SUMO_CONFIG = (
    PROJECT_ROOT
    / "simulation"
    / "config"
    / "ecotwin.sumocfg"
)

RESULTS_DIR = PROJECT_ROOT / "data" / "results"
RESULT_FILE = RESULTS_DIR / "baseline_metrics.json"


def main() -> None:
    if not SUMO_CONFIG.exists():
        raise FileNotFoundError(
            f"SUMO configuration not found: {SUMO_CONFIG}"
        )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    sumo_command = [
        "sumo",
        "-c",
        str(SUMO_CONFIG),
    ]

    print("=" * 70)
    print("EcoTwin Fixed-Time Baseline Evaluation")
    print("=" * 70)

    traci.start(sumo_command)

    total_co2_mg = 0.0
    total_speed = 0.0
    speed_samples = 0

    total_waiting_time = 0.0

    departed_vehicles = 0
    arrived_vehicles = 0

    unique_vehicle_ids: set[str] = set()

    step_count = 0

    try:
        step_length = traci.simulation.getDeltaT()

        print(f"Simulation step length: {step_length:.2f} s")
        print("Running baseline simulation...\n")

        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            step_count += 1

            vehicle_ids = list(traci.vehicle.getIDList())

            departed_ids = traci.simulation.getDepartedIDList()
            arrived_ids = traci.simulation.getArrivedIDList()

            departed_vehicles += len(departed_ids)
            arrived_vehicles += len(arrived_ids)

            unique_vehicle_ids.update(vehicle_ids)
            unique_vehicle_ids.update(departed_ids)

            for vehicle_id in vehicle_ids:
                speed = traci.vehicle.getSpeed(vehicle_id)

                co2_mg_per_second = (
                    traci.vehicle.getCO2Emission(vehicle_id)
                )

                waiting_time = (
                    traci.vehicle.getWaitingTime(vehicle_id)
                )

                # CO2 from TraCI is instantaneous mg/s.
                # Multiply by simulation step length to obtain mg
                # emitted during this timestep.
                total_co2_mg += (
                    co2_mg_per_second * step_length
                )

                total_speed += speed
                speed_samples += 1

                # SUMO waiting time is > 0 while a vehicle
                # is considered to be waiting.
                if waiting_time > 0:
                    total_waiting_time += step_length

            if step_count % 100 == 0:
                simulation_time = (
                    traci.simulation.getTime()
                )

                print(
                    f"Time={simulation_time:7.1f}s | "
                    f"Active={len(vehicle_ids):3d} | "
                    f"Departed={departed_vehicles:3d} | "
                    f"Arrived={arrived_vehicles:3d}"
                )

    finally:
        final_simulation_time = traci.simulation.getTime()
        traci.close()

    total_co2_g = total_co2_mg / 1000.0

    if speed_samples > 0:
        average_speed_mps = total_speed / speed_samples
    else:
        average_speed_mps = 0.0

    average_speed_kmh = average_speed_mps * 3.6

    unique_vehicle_count = len(unique_vehicle_ids)

    if unique_vehicle_count > 0:
        average_waiting_time = (
            total_waiting_time / unique_vehicle_count
        )
    else:
        average_waiting_time = 0.0

    metrics = {
        "controller": "SUMO fixed-time",
        "simulation_time_seconds": round(
            final_simulation_time,
            2,
        ),
        "simulation_steps": step_count,
        "unique_vehicles": unique_vehicle_count,
        "departed_vehicles": departed_vehicles,
        "completed_trips": arrived_vehicles,
        "total_co2_mg": round(total_co2_mg, 2),
        "total_co2_g": round(total_co2_g, 3),
        "total_waiting_time_seconds": round(
            total_waiting_time,
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
    }

    with RESULT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metrics,
            file,
            indent=4,
        )

    print("\n" + "=" * 70)
    print("BASELINE RESULTS")
    print("=" * 70)

    print(
        f"Simulation duration : "
        f"{metrics['simulation_time_seconds']:.2f} s"
    )

    print(
        f"Unique vehicles     : "
        f"{metrics['unique_vehicles']}"
    )

    print(
        f"Departed vehicles   : "
        f"{metrics['departed_vehicles']}"
    )

    print(
        f"Completed trips     : "
        f"{metrics['completed_trips']}"
    )

    print(
        f"Total CO2           : "
        f"{metrics['total_co2_g']:.3f} g"
    )

    print(
        f"Total waiting time  : "
        f"{metrics['total_waiting_time_seconds']:.2f} s"
    )

    print(
        f"Avg waiting time    : "
        f"{metrics['average_waiting_time_seconds']:.3f} s/vehicle"
    )

    print(
        f"Average speed       : "
        f"{metrics['average_speed_mps']:.3f} m/s "
        f"({metrics['average_speed_kmh']:.3f} km/h)"
    )

    print("=" * 70)

    print(
        f"\nResults saved to:\n"
        f"{RESULT_FILE}"
    )


if __name__ == "__main__":
    main()