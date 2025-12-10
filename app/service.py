from fastapi import APIRouter, HTTPException
from app.model import get_model, reload_model
from app.schemas import (
    ChangeInput,
    ScoreResponse,
    HealthResponse,
    ReloadResponse,
)

router = APIRouter()


@router.post("/score-change", response_model=ScoreResponse)
def score_change(input_data: ChangeInput):
    """
    Score a change request using the scorecardpy-based model.

    Returns explainable score with per-feature breakdown.

    The score is calculated by:
    1. Matching each input feature to its scorecard bin
    2. Summing the points from all features
    3. Adding the base score (default 600)
    4. Mapping to a risk band
    """
    try:
        model = get_model()
        result = model.score(input_data.model_dump())
        return result
    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid value for feature: {e}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload-config", response_model=ReloadResponse)
def reload_config():
    """
    Hot-reload the scorecard configuration.

    Use this endpoint to reload the YAML config without restarting the service.
    """
    try:
        reload_model()
        model = get_model()
        return {
            "status": "reloaded",
            "version": model.version,
            "features": model.get_features()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
def health():
    """Health check with config version."""
    model = get_model()
    return {
        "status": "healthy",
        "version": model.version,
        "score_name": model.score_name
    }


@router.get("/scorecard")
def get_scorecard():
    """
    Return the current scorecard definition for transparency.

    This endpoint exposes the full scorecard configuration including:
    - All features and their bins
    - Points assigned to each bin
    - Risk band thresholds
    """
    model = get_model()
    return {
        "version": model.version,
        "base_points": model.base_points,
        "scorecard": model.scorecard_df.to_dict(orient="records"),
        "bands": model.bands
    }
