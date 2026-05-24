from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REASON_CODE_MAP = {
    "debt_to_income": "Elevated debt-to-income ratio",
    "revolving_utilization": "High revolving credit utilization",
    "delinquency_count": "Recent or repeated delinquency history",
    "delinquency_per_year": "High delinquency rate relative to credit history",
    "loan_to_income": "Requested loan amount is high relative to income",
    "interest_rate": "Higher priced credit product indicates elevated risk",
    "thin_file_flag": "Limited credit history",
    "credit_history_years": "Shorter credit history",
}


@dataclass
class ExplanationResult:
    top_features: list[dict[str, float | str]]
    reason_codes: list[str]
    method: str


class CreditRiskExplainer:
    """Generate local explanations with SHAP when available and stable fallbacks otherwise."""

    def explain_instance(self, model: Any, features: pd.DataFrame, top_n: int = 5) -> ExplanationResult:
        try:
            import shap

            explainer = shap.Explainer(model.predict_proba, features)
            shap_values = explainer(features)
            values = np.asarray(shap_values.values)
            if values.ndim == 3:
                contributions = values[0, :, 1]
            else:
                contributions = values[0]
            method = "shap"
        except Exception:
            contributions = self._fallback_importance(model, features)
            method = "model_importance_fallback"

        feature_rows = []
        for column, contribution in zip(features.columns, contributions):
            feature_rows.append({"feature": column, "contribution": float(contribution)})
        feature_rows = sorted(feature_rows, key=lambda item: abs(item["contribution"]), reverse=True)[:top_n]

        reason_codes = self._reason_codes(feature_rows)
        return ExplanationResult(top_features=feature_rows, reason_codes=reason_codes, method=method)

    def _fallback_importance(self, model: Any, features: pd.DataFrame) -> np.ndarray:
        estimator = model.steps[-1][1] if hasattr(model, "steps") else model
        if hasattr(estimator, "feature_importances_"):
            return np.asarray(estimator.feature_importances_)
        if hasattr(estimator, "coef_"):
            return np.asarray(estimator.coef_[0])
        return np.zeros(features.shape[1])

    def _reason_codes(self, feature_rows: list[dict[str, float | str]]) -> list[str]:
        codes: list[str] = []
        for row in feature_rows:
            feature = str(row["feature"])
            base_feature = next((key for key in REASON_CODE_MAP if feature.startswith(key)), None)
            if base_feature and float(row["contribution"]) > 0:
                codes.append(REASON_CODE_MAP[base_feature])
        return codes[:3] or ["No dominant adverse driver identified"]


def generate_global_explainability_artifact(model: Any, features: pd.DataFrame, output_dir: Path, top_n: int = 15) -> dict[str, Any]:
    """Persist global model importance for governance and review workflows."""
    estimator = model.steps[-1][1] if hasattr(model, "steps") else model
    method = "model_feature_importance"

    if hasattr(estimator, "feature_importances_"):
        values = np.asarray(estimator.feature_importances_)
    elif hasattr(estimator, "coef_"):
        values = np.abs(np.asarray(estimator.coef_[0]))
        method = "absolute_model_coefficients"
    else:
        values = np.zeros(features.shape[1])
        method = "unavailable"

    total = values.sum()
    normalized = values / total if total > 0 else values
    rows = [
        {
            "feature": column,
            "importance": float(importance),
            "business_reason": REASON_CODE_MAP.get(column, "Model-derived risk signal"),
        }
        for column, importance in zip(features.columns, normalized)
    ]
    rows = sorted(rows, key=lambda row: row["importance"], reverse=True)[:top_n]
    artifact = {
        "method": method,
        "top_features": rows,
        "governance_note": (
            "Global importance supports model review and stakeholder interpretation. "
            "Borrower-level decisions should use local explanations from the scoring API."
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "global_explainability.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    return artifact
