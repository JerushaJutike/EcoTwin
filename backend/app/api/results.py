from fastapi import APIRouter

from backend.app.services.results_service import (
    load_comparison_results,
)


router = APIRouter(
    prefix="/api/results",
    tags=["Results"],
)


@router.get("/comparison")
def get_comparison_results():
    """
    Return baseline vs RL comparison results.
    """

    return load_comparison_results()