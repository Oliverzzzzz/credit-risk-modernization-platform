from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from src.data_ingestion.mappings import DatasetMapping, MAPPING_REGISTRY
from src.preprocessing.schema import REQUIRED_COLUMNS, TARGET_COLUMN, TRAINING_COLUMNS


DEFAULT_STATUSES = {"DEFAULT", "CHARGED OFF", "LATE (31-120 DAYS)", "DOES NOT MEET THE CREDIT POLICY. STATUS:CHARGED OFF"}
NON_DEFAULT_STATUSES = {"CURRENT", "FULLY PAID", "ISSUED", "IN GRACE PERIOD"}


def available_mappings() -> list[str]:
    return sorted(MAPPING_REGISTRY)


def load_credit_dataset(path: str | Path, mapping_name: str = "canonical", require_target: bool = True) -> pd.DataFrame:
    source = pd.read_csv(path)
    mapping = _mapping_for(mapping_name)
    canonical = map_to_canonical_schema(source, mapping, require_target=require_target)
    validate_canonical_schema(canonical, require_target=require_target)
    return canonical


def map_to_canonical_schema(data: pd.DataFrame, mapping: DatasetMapping, require_target: bool = True) -> pd.DataFrame:
    if mapping.name == "canonical":
        canonical = data.copy()
    else:
        canonical = pd.DataFrame(index=data.index)
        for canonical_column, source_column in mapping.columns.items():
            if source_column not in data.columns:
                if canonical_column in mapping.defaults:
                    canonical[canonical_column] = mapping.defaults[canonical_column]
                    continue
                if canonical_column == TARGET_COLUMN and not require_target:
                    continue
                raise ValueError(f"Source column '{source_column}' required for '{canonical_column}' is missing.")
            canonical[canonical_column] = data[source_column]

        for column, value in mapping.defaults.items():
            if column not in canonical:
                canonical[column] = value

    canonical = _standardize_common_fields(canonical)
    if "MonthlyIncome" in data.columns and mapping.name == "give_me_some_credit":
        canonical["annual_income"] = pd.to_numeric(data["MonthlyIncome"], errors="coerce") * 12

    for column in mapping.percent_columns:
        if column in canonical:
            canonical[column] = _normalize_percent_series(canonical[column])

    if TARGET_COLUMN in canonical:
        canonical[TARGET_COLUMN] = _normalize_target(canonical[TARGET_COLUMN])

    ordered_columns = TRAINING_COLUMNS if require_target else REQUIRED_COLUMNS
    return canonical[[column for column in ordered_columns if column in canonical.columns]]


def validate_canonical_schema(data: pd.DataFrame, require_target: bool = True) -> None:
    expected = set(TRAINING_COLUMNS if require_target else REQUIRED_COLUMNS)
    missing = sorted(expected - set(data.columns))
    if missing:
        raise ValueError(f"Mapped dataset is missing canonical columns: {missing}")


def _mapping_for(mapping_name: str) -> DatasetMapping:
    try:
        return MAPPING_REGISTRY[mapping_name]
    except KeyError as exc:
        raise ValueError(f"Unknown mapping '{mapping_name}'. Available mappings: {available_mappings()}") from exc


def _standardize_common_fields(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    if "employment_length_years" in frame:
        frame["employment_length_years"] = frame["employment_length_years"].apply(_parse_years)
    return frame


def _parse_years(value: object) -> float:
    if pd.isna(value):
        return 0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().lower()
    if text.startswith("<"):
        return 0.5
    if text.startswith("10+"):
        return 10.0
    match = re.search(r"(\d+)", text)
    return float(match.group(1)) if match else 0.0


def _normalize_percent_series(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.replace("%", "", regex=False)
    numeric = pd.to_numeric(cleaned, errors="coerce")
    return numeric.where(numeric <= 1, numeric / 100)


def _normalize_target(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce").fillna(0).astype(int)

    normalized = series.fillna("").astype(str).str.strip().str.upper()
    target = normalized.map(lambda value: 1 if value in DEFAULT_STATUSES else 0 if value in NON_DEFAULT_STATUSES else 0)
    return target.astype(int)
