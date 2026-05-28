from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from src.monitoring.metrics import ApiMetrics
from src.scoring.service import CreditRiskScoringService, artifact_paths

MAX_BATCH_SIZE = 100
ALLOWED_HOME_OWNERSHIP = {"MORTGAGE", "OWN", "RENT", "UNKNOWN"}
ALLOWED_LOAN_PURPOSE = {"debt_consolidation", "home_improvement", "small_business", "medical", "major_purchase", "UNKNOWN"}


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

    @field_validator("home_ownership")
    @classmethod
    def validate_home_ownership(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in ALLOWED_HOME_OWNERSHIP:
            raise ValueError(f"home_ownership must be one of {sorted(ALLOWED_HOME_OWNERSHIP)}")
        return normalized

    @field_validator("loan_purpose")
    @classmethod
    def validate_loan_purpose(cls, value: str) -> str:
        normalized = value.lower()
        if normalized.upper() == "UNKNOWN":
            return "UNKNOWN"
        if normalized not in ALLOWED_LOAN_PURPOSE:
            raise ValueError(f"loan_purpose must be one of {sorted(ALLOWED_LOAN_PURPOSE)}")
        return normalized


class BatchPayload(BaseModel):
    applicants: list[ApplicantPayload] = Field(min_length=1, max_length=MAX_BATCH_SIZE)


app = FastAPI(
    title="Credit Risk Modernization Platform",
    description="Enterprise-style explainable credit risk scoring API.",
    version="0.1.0",
)

metrics = ApiMetrics()
scoring_service = CreditRiskScoringService()


def _request_id(request: Request) -> str:
    return request.headers.get("X-Request-ID", str(uuid4()))


def _error_response(code: str, message: str, request_id: str, status_code: int, details: Any | None = None) -> JSONResponse:
    payload: dict[str, Any] = {"error": {"code": code, "message": message, "request_id": request_id}}
    if details is not None:
        payload["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=payload, headers={"X-Request-ID": request_id})


def _safe_validation_errors(exc: RequestValidationError) -> list[dict[str, Any]]:
    safe_errors = []
    for error in exc.errors():
        safe_error = dict(error)
        if "ctx" in safe_error:
            safe_error["ctx"] = {key: str(value) for key, value in safe_error["ctx"].items()}
        safe_errors.append(safe_error)
    return safe_errors


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return _error_response(
        code="VALIDATION_ERROR",
        message="Request validation failed.",
        request_id=_request_id(request),
        status_code=422,
        details=_safe_validation_errors(exc),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return _error_response(
        code="HTTP_ERROR",
        message=str(exc.detail),
        request_id=_request_id(request),
        status_code=exc.status_code,
    )


@app.middleware("http")
async def add_request_id_header(request: Request, call_next):
    request_id = _request_id(request)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


def _score_payload(payload: ApplicantPayload) -> dict[str, Any]:
    response = scoring_service.score_record(payload.model_dump())
    metrics.record_prediction(response["risk_tier"], response["risk_probability"])
    return response


@app.get("/health")
def health() -> dict[str, Any]:
    metrics.health_check_count += 1
    paths = artifact_paths()
    artifacts = {name: path.exists() for name, path in paths.items()}
    return {
        "status": "ok",
        "model_available": artifacts["model"],
        "artifacts": artifacts,
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
