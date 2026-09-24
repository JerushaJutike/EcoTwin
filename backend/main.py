from __future__ import annotations

import asyncio

from fastapi import (
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware

from backend.services.results_service import (
    get_all_results,
    get_result,
)

from backend.services.simulation_service import (
    simulation_service,
)


app = FastAPI(
    title="EcoTwin API",
    description=(
        "Backend API for the EcoTwin urban traffic "
        "and carbon optimization platform."
    ),
    version="0.2.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    return {
        "name": "EcoTwin API",
        "version": "0.2.0",
        "status": "running",
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
    }


@app.get("/api/status")
def project_status() -> dict:
    return {
        "project": "EcoTwin",
        "simulation": "SUMO",
        "controller": "PPO",
        "backend": "FastAPI",
        "websocket": True,
        "status": "ready",
    }


@app.get("/api/results")
def all_results() -> dict:
    return get_all_results()


@app.get("/api/results/{result_type}")
def result_by_type(
    result_type: str,
) -> dict:
    try:
        return get_result(
            result_type
        )

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Unknown result type: "
                f"{result_type}"
            ),
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@app.get("/api/simulation/status")
def simulation_status() -> dict:
    return simulation_service.get_status()


@app.post("/api/simulation/start")
def start_simulation() -> dict:
    started = simulation_service.start()

    if not started:
        raise HTTPException(
            status_code=409,
            detail=(
                "Simulation is already running."
            ),
        )

    return {
        "message": "Simulation started.",
    }


@app.post("/api/simulation/stop")
def stop_simulation() -> dict:
    stopped = simulation_service.stop()

    if not stopped:
        raise HTTPException(
            status_code=409,
            detail=(
                "Simulation is not running."
            ),
        )

    return {
        "message": (
            "Simulation stop requested."
        ),
    }


@app.post(
    "/api/simulation/controller/{controller}"
)
def set_simulation_controller(
    controller: str,
) -> dict:
    try:
        simulation_service.set_controller(
            controller
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )

    return {
        "message": (
            f"Controller set to "
            f"{controller}."
        ),
        "controller": controller,
    }


@app.websocket("/ws/simulation")
async def simulation_websocket(
    websocket: WebSocket,
) -> None:
    await websocket.accept()

    try:
        while True:
            snapshot = (
                simulation_service.get_status()
            )

            await websocket.send_json(
                snapshot
            )

            await asyncio.sleep(
                0.25
            )

    except WebSocketDisconnect:
        pass