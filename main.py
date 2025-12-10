from fastapi import FastAPI
from app.service import router as scoring_router

app = FastAPI(
    title="Change Risk Scorecard Service",
    description="Risk scoring service using scorecardpy for change management",
    version="1.0.0",
)

app.include_router(scoring_router, tags=["scoring"])


@app.on_event("startup")
async def startup():
    """Validate scorecard loads correctly on startup."""
    from app.model import get_model
    model = get_model()
    print(f"Loaded scorecard v{model.version} with {len(model.scorecard_df)} bins")
    print(f"Features: {model.get_features()}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
