from __future__ import annotations

import pandas as pd

from src.preprocessing.schema import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, REQUIRED_COLUMNS, TARGET_COLUMN


class CreditDataPreprocessor:
    """Validate and clean applicant records before feature engineering."""

    def __init__(self, require_target: bool = False) -> None:
        self.require_target = require_target

    def validate_schema(self, data: pd.DataFrame) -> None:
        required = list(REQUIRED_COLUMNS)
        if self.require_target:
            required.append(TARGET_COLUMN)
        missing = sorted(set(required) - set(data.columns))
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        self.validate_schema(data)
        frame = data.copy()

        for column in NUMERIC_COLUMNS:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
            frame[column] = frame[column].fillna(frame[column].median())

        frame["annual_income"] = frame["annual_income"].clip(lower=1)
        frame["debt_to_income"] = frame["debt_to_income"].clip(lower=0, upper=1.5)
        frame["interest_rate"] = frame["interest_rate"].clip(lower=0, upper=1)
        frame["revolving_utilization"] = frame["revolving_utilization"].clip(lower=0, upper=1.5)
        frame["loan_amount"] = frame["loan_amount"].clip(lower=0)

        for column in CATEGORICAL_COLUMNS:
            frame[column] = frame[column].fillna("UNKNOWN").astype(str).str.upper()

        if self.require_target:
            frame[TARGET_COLUMN] = pd.to_numeric(frame[TARGET_COLUMN], errors="coerce").fillna(0).astype(int)

        return frame

    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        return self.transform(data)
