from fastapi import FastAPI

from backend.app.api.results import router as results_router


app = FastAPI(
    title="EcoTwin API",
    description="Backend API for EcoTwin reinforcement learning traffic optimization.",
    version="1.0.0",
)


app.include_router(results_router)


@app.get("/")
def root():
    return {
        "project": "EcoTwin",
        "status": "API is running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }