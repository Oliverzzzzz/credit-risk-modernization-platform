from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.monitoring.metrics import ApiMetrics
from src.scoring.service import CreditRiskScoringService, artifact_paths


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
scoring_service = CreditRiskScoringService()


def _score_payload(payload: ApplicantPayload) -> dict[str, Any]:
    response = scoring_service.score_record(payload.model_dump())
    metrics.record_prediction(response["risk_tier"], response["risk_probability"])
    return response


@app.get("/health")
def health() -> dict[str, Any]:
    metrics.health_check_count += 1
    paths = artifact_paths()
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
