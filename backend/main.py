from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.services.results_service import (
    get_all_results,
    get_result,
)


app = FastAPI(
    title="EcoTwin API",
    description=(
        "Backend API for the EcoTwin urban traffic "
        "and carbon optimization platform."
    ),
    version="0.1.0",
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
        "version": "0.1.0",
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