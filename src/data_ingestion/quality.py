from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.preprocessing.schema import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, REQUIRED_COLUMNS, TARGET_COLUMN
from src.utils.paths import REPORT_ARTIFACT_DIR, ensure_project_directories


NUMERIC_RANGES = {
    "annual_income": {"min": 1, "max": 1_000_000},
    "debt_to_income": {"min": 0, "max": 1.5},
    "loan_amount": {"min": 0, "max": 500_000},
    "interest_rate": {"min": 0, "max": 1},
    "employment_length_years": {"min": 0, "max": 60},
    "credit_history_years": {"min": 0, "max": 80},
    "delinquency_count": {"min": 0, "max": 50},
    "revolving_utilization": {"min": 0, "max": 1.5},
    "open_credit_lines": {"min": 0, "max": 100},
}


def generate_data_quality_report(data: pd.DataFrame, require_target: bool = True) -> dict[str, Any]:
    expected_columns = REQUIRED_COLUMNS + ([TARGET_COLUMN] if require_target else [])
    missing_columns = sorted(set(expected_columns) - set(data.columns))
    report = {
        "row_count": int(len(data)),
        "column_count": int(len(data.columns)),
        "missing_columns": missing_columns,
        "missing_values": _missing_value_summary(data),
        "numeric_ranges": _numeric_range_summary(data),
        "categorical_distributions": _categorical_distribution_summary(data),
        "target_balance": _target_balance_summary(data) if TARGET_COLUMN in data.columns else None,
        "status": "pass",
    }
    report["status"] = "fail" if missing_columns or _has_range_violations(report["numeric_ranges"]) else "pass"
    return report


def write_data_quality_report(data: pd.DataFrame, output_path: Path | None = None, require_target: bool = True) -> dict[str, Any]:
    ensure_project_directories()
    report = generate_data_quality_report(data, require_target=require_target)
    destination = output_path or REPORT_ARTIFACT_DIR / "data_quality_report.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def _missing_value_summary(data: pd.DataFrame) -> dict[str, dict[str, float | int]]:
    row_count = max(len(data), 1)
    return {
        column: {
            "missing_count": int(data[column].isna().sum()),
            "missing_rate": float(data[column].isna().sum() / row_count),
        }
        for column in data.columns
    }


def _numeric_range_summary(data: pd.DataFrame) -> dict[str, dict[str, float | int | None]]:
    summary: dict[str, dict[str, float | int | None]] = {}
    for column in NUMERIC_COLUMNS:
        if column not in data.columns:
            continue
        numeric = pd.to_numeric(data[column], errors="coerce")
        rules = NUMERIC_RANGES[column]
        below_min = int((numeric < rules["min"]).sum())
        above_max = int((numeric > rules["max"]).sum())
        summary[column] = {
            "min": float(numeric.min()) if not numeric.dropna().empty else None,
            "max": float(numeric.max()) if not numeric.dropna().empty else None,
            "below_min_count": below_min,
            "above_max_count": above_max,
            "expected_min": rules["min"],
            "expected_max": rules["max"],
        }
    return summary


def _categorical_distribution_summary(data: pd.DataFrame) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for column in CATEGORICAL_COLUMNS:
        if column in data.columns:
            counts = data[column].fillna("MISSING").astype(str).value_counts(dropna=False).head(20)
            summary[column] = {str(category): int(count) for category, count in counts.items()}
    return summary


def _target_balance_summary(data: pd.DataFrame) -> dict[str, float | int]:
    target = pd.to_numeric(data[TARGET_COLUMN], errors="coerce").fillna(0).astype(int)
    positive_count = int((target == 1).sum())
    negative_count = int((target == 0).sum())
    total = max(len(target), 1)
    return {
        "positive_count": positive_count,
        "negative_count": negative_count,
        "positive_rate": float(positive_count / total),
    }


def _has_range_violations(numeric_ranges: dict[str, dict[str, float | int | None]]) -> bool:
    return any(summary["below_min_count"] > 0 or summary["above_max_count"] > 0 for summary in numeric_ranges.values())
