from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.metrics_store import load_metrics
from app.ml import find_comparables, load_artifacts, predict_ranges
from app.schemas import MetricsResponse, TrainRequest, TrainResponse, ValuationRequest, ValuationResponse
from app.train import run_training

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MODEL_PATH = f"{settings.model_dir}/model.joblib"


@app.get("/metrics", response_model=MetricsResponse)
def get_metrics() -> MetricsResponse:
    metrics = load_metrics(settings.metrics_path)
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found. Train the model first.")
    return MetricsResponse(metrics=metrics)


@app.post("/train", response_model=TrainResponse)
def train_endpoint(payload: TrainRequest) -> TrainResponse:
    if not Path(payload.data_path).exists():
        raise HTTPException(status_code=400, detail="Data path not found.")
    metrics, rows = run_training(payload.data_path)
    return TrainResponse(status="trained", rows_used=rows, metrics=metrics)


@app.post("/value", response_model=ValuationResponse)
def value_endpoint(payload: ValuationRequest) -> ValuationResponse:
    if not Path(MODEL_PATH).exists():
        raise HTTPException(
            status_code=400,
            detail="Model not trained. Run the training job via POST /train or CLI.",
        )
    artifacts = load_artifacts(MODEL_PATH)
    payload_dict = payload.model_dump()
    ranges = predict_ranges(artifacts, payload_dict)
    comps = find_comparables(artifacts, payload_dict)

    suburb_note = (
        "Suburb has limited training data. Falling back to Central Coast model."
        if payload.suburb not in artifacts.suburb_encoding
        else ""
    )

    tiers = [
        {
            "tier": tier,
            "point_estimate": values["point"],
            "interval_50": [values["low50"], values["high50"]],
            "interval_80": [values["low80"], values["high80"]],
        }
        for tier, values in ranges.items()
    ]

    explanation = {
        "top_drivers": [
            "Beds, baths, and land size",
            "Recent Central Coast price trend",
            "Suburb price level",
            "Property type",
            "Feature signals (pool, solar, views)",
        ],
        "comparable_sales": comps,
        "sensitivity": [
            "Condition tier adjustments",
            "Market volatility and seasonality",
            "Limited comparable sales",
        ],
        "confidence_notes": list(
            filter(
                None,
                [
                    "Intervals widen when recent data is sparse.",
                    suburb_note,
                    "Outliers are winsorized to reduce volatility.",
                ],
            )
        ),
    }

    return ValuationResponse(
        tiers=tiers,
        explanation=explanation,
        disclaimer="Not financial advice. Estimates are uncertain and depend on data quality.",
        data_sources=[
            "NSW Valuer General Property Sales Data Files",
            "Domain APIs (optional integration if keys provided)",
        ],
    )
