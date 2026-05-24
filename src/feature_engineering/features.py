from __future__ import annotations

import pandas as pd


class CreditFeatureEngineer:
    """Generate business-oriented features for credit risk modeling."""

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        frame = data.copy()
        frame["loan_to_income"] = frame["loan_amount"] / frame["annual_income"].clip(lower=1)
        frame["credit_line_density"] = frame["open_credit_lines"] / frame["credit_history_years"].clip(lower=1)
        frame["delinquency_per_year"] = frame["delinquency_count"] / frame["credit_history_years"].clip(lower=1)
        frame["high_utilization_flag"] = (frame["revolving_utilization"] >= 0.75).astype(int)
        frame["thin_file_flag"] = (frame["credit_history_years"] < 3).astype(int)
        frame["secured_home_flag"] = frame["home_ownership"].isin(["MORTGAGE", "OWN"]).astype(int)
        return pd.get_dummies(frame, columns=["home_ownership", "loan_purpose"], drop_first=False)

    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        return self.transform(data)


def align_features(data: pd.DataFrame, feature_names: list[str]) -> pd.DataFrame:
    aligned = data.copy()
    for column in feature_names:
        if column not in aligned.columns:
            aligned[column] = 0
    return aligned[feature_names]
