from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.evaluation.metrics import assign_risk_tier
from src.explainability.shap_explainer import CreditRiskExplainer
from src.feature_engineering.features import CreditFeatureEngineer, align_features
from src.monitoring.logging import PredictionLogger
from src.monitoring.metrics import ApiMetrics
from src.preprocessing.pipeline import CreditDataPreprocessor
from src.training.train_model import train_credit_risk_model
from src.utils.config import DEFAULT_MODEL_CONFIG
from src.utils.paths import MODEL_DIR, ensure_project_directories
from src.utils.sample_data import generate_credit_sample


class ApplicantPayload(BaseModel):
    annual_income: float = Field(gt=0)
    debt_to_income: float = Field(ge=0)
    loan_amount: float = Field(gt=0)
    interest_rate: float = Field(ge=0, le=1)
    employment_length_years: int = Field(ge=0)
    credit_history_years: int = Field(ge=0)
    delinquency_count: int = Field(ge=0)
    revolving_utilization: float = Field(ge=0)
    open_credit_lines: int = Field(ge=0)
    home_ownership: str
    loan_purpose: str


class BatchPayload(BaseModel):
    applicants: list[ApplicantPayload]


app = FastAPI(
    title="Credit Risk Modernization Platform",
    description="Enterprise-style explainable credit risk scoring API.",
    version="0.1.0",
)

metrics = ApiMetrics()
prediction_logger = PredictionLogger()
explainer = CreditRiskExplainer()


def _artifact_paths() -> dict[str, Path]:
    return {
        "model": MODEL_DIR / "credit_risk_model.joblib",
        "metadata": MODEL_DIR / "model_metadata.json",
        "features": MODEL_DIR / "feature_schema.json",
    }


def _ensure_model_artifacts() -> None:
    ensure_project_directories()
    paths = _artifact_paths()
    if not paths["model"].exists():
        train_credit_risk_model(generate_credit_sample(rows=900), MODEL_DIR)


def _load_artifacts() -> tuple[Any, dict[str, Any], list[str]]:
    _ensure_model_artifacts()
    paths = _artifact_paths()
    model = joblib.load(paths["model"])
    metadata = json.loads(paths["metadata"].read_text(encoding="utf-8"))
    feature_schema = json.loads(paths["features"].read_text(encoding="utf-8"))
    return model, metadata, feature_schema["features"]


def _prepare_features(payloads: list[ApplicantPayload], feature_names: list[str]) -> pd.DataFrame:
    raw = pd.DataFrame([payload.model_dump() for payload in payloads])
    clean = CreditDataPreprocessor(require_target=False).transform(raw)
    engineered = CreditFeatureEngineer().transform(clean)
    return align_features(engineered, feature_names)


def _score_payload(payload: ApplicantPayload) -> dict[str, Any]:
    model, metadata, feature_names = _load_artifacts()
    features = _prepare_features([payload], feature_names)
    probability = float(model.predict_proba(features)[:, 1][0])
    threshold_policy = metadata.get("threshold_policy", {})
    tier = assign_risk_tier(
        probability,
        low_max=DEFAULT_MODEL_CONFIG.thresholds.low_max,
        medium_max=DEFAULT_MODEL_CONFIG.thresholds.medium_max,
    )
    explanation = explainer.explain_instance(model, features)
    response = {
        "risk_probability": round(probability, 6),
        "risk_tier": tier,
        "model_version": metadata["model_version"],
        "model_name": metadata["model_name"],
        "decision_threshold": threshold_policy.get("optimized_threshold", 0.5),
        "reason_codes": explanation.reason_codes,
        "top_features": explanation.top_features,
        "explanation_method": explanation.method,
        "scored_at": datetime.now(UTC).isoformat(),
    }
    metrics.record_prediction(tier)
    prediction_logger.write(
        {
            "risk_probability": response["risk_probability"],
            "risk_tier": tier,
            "model_version": metadata["model_version"],
            "request": payload.model_dump(),
        }
    )
    return response


@app.get("/health")
def health() -> dict[str, Any]:
    metrics.health_check_count += 1
    paths = _artifact_paths()
    return {
        "status": "ok",
        "model_available": paths["model"].exists(),
        "service": "credit-risk-modernization-platform",
        "checked_at": datetime.now(UTC).isoformat(),
    }


@app.post("/predict")
def predict(payload: ApplicantPayload) -> dict[str, Any]:
    return _score_payload(payload)


@app.post("/batch_predict")
def batch_predict(payload: BatchPayload) -> dict[str, Any]:
    predictions = [_score_payload(applicant) for applicant in payload.applicants]
    metrics.record_batch(len(payload.applicants))
    return {"predictions": predictions, "count": len(predictions)}


@app.get("/metrics")
def get_metrics() -> dict[str, Any]:
    return metrics.as_dict()
