from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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