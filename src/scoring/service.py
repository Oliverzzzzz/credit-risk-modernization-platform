from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.evaluation.metrics import assign_risk_tier
from src.explainability.shap_explainer import CreditRiskExplainer
from src.feature_engineering.features import CreditFeatureEngineer, align_features
from src.monitoring.logging import PredictionLogger
from src.preprocessing.pipeline import CreditDataPreprocessor
from src.training.train_model import train_credit_risk_model
from src.utils.config import DEFAULT_MODEL_CONFIG
from src.utils.paths import MODEL_DIR, ensure_project_directories
from src.utils.sample_data import generate_credit_sample


def artifact_paths(model_dir: Path = MODEL_DIR) -> dict[str, Path]:
    return {
        "model": model_dir / "credit_risk_model.joblib",
        "metadata": model_dir / "model_metadata.json",
        "features": model_dir / "feature_schema.json",
    }


def ensure_model_artifacts(model_dir: Path = MODEL_DIR) -> None:
    ensure_project_directories()
    paths = artifact_paths(model_dir)
    if not paths["model"].exists():
        train_credit_risk_model(generate_credit_sample(rows=900), model_dir)


def load_artifacts(model_dir: Path = MODEL_DIR) -> tuple[Any, dict[str, Any], list[str]]:
    ensure_model_artifacts(model_dir)
    paths = artifact_paths(model_dir)
    model = joblib.load(paths["model"])
    metadata = json.loads(paths["metadata"].read_text(encoding="utf-8"))
    feature_schema = json.loads(paths["features"].read_text(encoding="utf-8"))
    return model, metadata, feature_schema["features"]


class CreditRiskScoringService:
    def __init__(
        self,
        model_dir: Path = MODEL_DIR,
        prediction_logger: PredictionLogger | None = None,
        explainer: CreditRiskExplainer | None = None,
    ) -> None:
        self.model, self.metadata, self.feature_names = load_artifacts(model_dir)
        self.prediction_logger = prediction_logger or PredictionLogger()
        self.explainer = explainer or CreditRiskExplainer()

    def prepare_features(self, records: pd.DataFrame) -> pd.DataFrame:
        clean = CreditDataPreprocessor(require_target=False).transform(records)
        engineered = CreditFeatureEngineer().transform(clean)
        return align_features(engineered, self.feature_names)

    def score_records(self, records: pd.DataFrame, include_explanations: bool = True, log_predictions: bool = True) -> list[dict[str, Any]]:
        features = self.prepare_features(records)
        probabilities = self.model.predict_proba(features)[:, 1]
        responses: list[dict[str, Any]] = []
        for row_index, probability in enumerate(probabilities):
            response = self._build_response(float(probability), features.iloc[[row_index]], include_explanations)
            if log_predictions:
                self.prediction_logger.write(
                    {
                        "risk_probability": response["risk_probability"],
                        "risk_tier": response["risk_tier"],
                        "model_version": response["model_version"],
                        "request": records.iloc[row_index].to_dict(),
                    }
                )
            responses.append(response)
        return responses

    def score_record(self, record: dict[str, Any], include_explanations: bool = True, log_predictions: bool = True) -> dict[str, Any]:
        return self.score_records(pd.DataFrame([record]), include_explanations=include_explanations, log_predictions=log_predictions)[0]

    def _build_response(self, probability: float, feature_row: pd.DataFrame, include_explanations: bool) -> dict[str, Any]:
        threshold_policy = self.metadata.get("threshold_policy", {})
        tier = assign_risk_tier(
            probability,
            low_max=DEFAULT_MODEL_CONFIG.thresholds.low_max,
            medium_max=DEFAULT_MODEL_CONFIG.thresholds.medium_max,
        )
        response: dict[str, Any] = {
            "risk_probability": round(probability, 6),
            "risk_tier": tier,
            "model_version": self.metadata["model_version"],
            "model_name": self.metadata["model_name"],
            "decision_threshold": threshold_policy.get("optimized_threshold", 0.5),
            "scored_at": datetime.now(UTC).isoformat(),
        }
        if include_explanations:
            explanation = self.explainer.explain_instance(self.model, feature_row)
            response["reason_codes"] = explanation.reason_codes
            response["top_features"] = explanation.top_features
            response["explanation_method"] = explanation.method
        return response
