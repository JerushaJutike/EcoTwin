from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.results import router as results_router


app = FastAPI(
    title="EcoTwin API",
    description="Backend API for EcoTwin urban traffic and carbon simulation",
    version="1.0.0",
)

# Allow the React/Vite frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(results_router)


@app.get("/")
def root():
    return {
        "project": "EcoTwin",
        "message": "EcoTwin API is running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }