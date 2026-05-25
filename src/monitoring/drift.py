from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import numpy as np

from src.preprocessing.schema import NUMERIC_COLUMNS
from src.utils.paths import REPORT_ARTIFACT_DIR, ensure_project_directories


def population_stability_index(reference: pd.Series, current: pd.Series, buckets: int = 10) -> float:
    quantiles = reference.quantile([i / buckets for i in range(1, buckets)]).drop_duplicates().to_list()
    reference_bins = pd.cut(reference, bins=[-float("inf"), *quantiles, float("inf")])
    current_bins = pd.cut(current, bins=[-float("inf"), *quantiles, float("inf")])
    ref_dist = reference_bins.value_counts(normalize=True).sort_index().replace(0, 0.0001)
    cur_dist = current_bins.value_counts(normalize=True).sort_index().replace(0, 0.0001)
    return float(((cur_dist - ref_dist) * np.log(cur_dist / ref_dist)).sum())


def drift_summary(reference: pd.DataFrame, current: pd.DataFrame, columns: list[str]) -> dict[str, float]:
    summary: dict[str, float] = {}
    for column in columns:
        if column in reference.columns and column in current.columns:
            summary[column] = population_stability_index(reference[column], current[column])
    return summary


def drift_band(psi_value: float) -> str:
    if psi_value < 0.10:
        return "stable"
    if psi_value < 0.25:
        return "moderate_drift"
    return "significant_drift"


def generate_drift_report(reference: pd.DataFrame, current: pd.DataFrame, columns: list[str] | None = None) -> dict[str, Any]:
    monitored_columns = columns or [column for column in NUMERIC_COLUMNS if column in reference.columns and column in current.columns]
    scores = drift_summary(reference, current, monitored_columns)
    feature_rows = [
        {
            "feature": feature,
            "psi": score,
            "status": drift_band(score),
        }
        for feature, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)
    ]
    overall_status = "stable"
    if any(row["status"] == "significant_drift" for row in feature_rows):
        overall_status = "significant_drift"
    elif any(row["status"] == "moderate_drift" for row in feature_rows):
        overall_status = "moderate_drift"

    return {
        "reference_row_count": int(len(reference)),
        "current_row_count": int(len(current)),
        "monitored_feature_count": len(feature_rows),
        "overall_status": overall_status,
        "features": feature_rows,
    }


def write_drift_report(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    output_path: Path | None = None,
    columns: list[str] | None = None,
) -> dict[str, Any]:
    ensure_project_directories()
    report = generate_drift_report(reference, current, columns=columns)
    destination = output_path or REPORT_ARTIFACT_DIR / "drift_report.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
