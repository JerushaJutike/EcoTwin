from fastapi import (
    APIRouter,
    HTTPException,
)

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

    try:
        return load_comparison_results()

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error