from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score


def evaluate_binary_classifier(y_true: np.ndarray, probabilities: np.ndarray, threshold: float = 0.5) -> dict[str, Any]:
    predictions = (probabilities >= threshold).astype(int)
    return {
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "precision": float(precision_score(y_true, predictions, zero_division=0)),
        "recall": float(recall_score(y_true, predictions, zero_division=0)),
        "f1": float(f1_score(y_true, predictions, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true, predictions).tolist(),
        "threshold": threshold,
    }


def optimize_threshold(y_true: np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
    """Select an operating threshold that balances recall and precision for review workflows."""
    candidate_thresholds = np.arange(0.20, 0.81, 0.05)
    scored_thresholds = []
    for threshold in candidate_thresholds:
        metrics = evaluate_binary_classifier(y_true, probabilities, float(threshold))
        scored_thresholds.append(
            {
                "threshold": float(threshold),
                "f1": metrics["f1"],
                "precision": metrics["precision"],
                "recall": metrics["recall"],
            }
        )
    best = max(scored_thresholds, key=lambda row: row["f1"])
    return {
        "default_threshold": 0.5,
        "optimized_threshold": best["threshold"],
        "optimization_metric": "f1",
        "precision_at_threshold": best["precision"],
        "recall_at_threshold": best["recall"],
        "f1_at_threshold": best["f1"],
    }


def assign_risk_tier(probability: float, low_max: float = 0.25, medium_max: float = 0.55) -> str:
    if probability < low_max:
        return "Low Risk"
    if probability < medium_max:
        return "Medium Risk"
    return "High Risk"
