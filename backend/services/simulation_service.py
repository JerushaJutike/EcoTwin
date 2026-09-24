from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

import traci


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SUMO_CONFIG = (
    PROJECT_ROOT
    / "simulation"
    / "config"
    / "ecotwin.sumocfg"
)


class SimulationService:
    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        self._state: dict[str, Any] = {
            "running": False,
            "simulation_time": 0.0,
            "active_vehicles": 0,
            "departed_vehicles": 0,
            "arrived_vehicles": 0,
            "status": "stopped",
        }

    def get_status(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._state)

    def start(self) -> bool:
        if (
            self._thread is not None
            and self._thread.is_alive()
        ):
            return False

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        self._thread.start()

        return True

    def stop(self) -> bool:
        if (
            self._thread is None
            or not self._thread.is_alive()
        ):
            return False

        self._stop_event.set()

        return True

    def _update_state(
        self,
        **values: Any,
    ) -> None:
        with self._lock:
            self._state.update(values)

    def _run(self) -> None:
        self._update_state(
            running=True,
            status="starting",
            simulation_time=0.0,
            active_vehicles=0,
            departed_vehicles=0,
            arrived_vehicles=0,
        )

        departed_total = 0
        arrived_total = 0

        try:
            traci.start(
                [
                    "sumo",
                    "-c",
                    str(SUMO_CONFIG),
                ]
            )

            self._update_state(
                status="running"
            )

            while (
                traci.simulation.getMinExpectedNumber()
                > 0
                and not self._stop_event.is_set()
            ):
                traci.simulationStep()

                departed_total += len(
                    traci.simulation.getDepartedIDList()
                )

                arrived_total += len(
                    traci.simulation.getArrivedIDList()
                )

                active_vehicles = len(
                    traci.vehicle.getIDList()
                )

                simulation_time = (
                    traci.simulation.getTime()
                )

                self._update_state(
                    simulation_time=simulation_time,
                    active_vehicles=active_vehicles,
                    departed_vehicles=departed_total,
                    arrived_vehicles=arrived_total,
                )

                # Slow it slightly so API clients can observe
                # the simulation progressing in real time.
                time.sleep(0.05)

            final_status = (
                "stopped"
                if self._stop_event.is_set()
                else "completed"
            )

            self._update_state(
                status=final_status,
            )

        except Exception as error:
            self._update_state(
                status="error",
                error=str(error),
            )

        finally:
            try:
                traci.close()
            except Exception:
                pass

            self._update_state(
                running=False,
            )


simulation_service = SimulationService()