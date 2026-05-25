from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DatasetMapping:
    name: str
    columns: dict[str, str]
    defaults: dict[str, object] = field(default_factory=dict)
    percent_columns: tuple[str, ...] = ()


LENDING_CLUB_MAPPING = DatasetMapping(
    name="lending_club",
    columns={
        "annual_income": "annual_inc",
        "debt_to_income": "dti",
        "loan_amount": "loan_amnt",
        "interest_rate": "int_rate",
        "employment_length_years": "emp_length",
        "delinquency_count": "delinq_2yrs",
        "revolving_utilization": "revol_util",
        "open_credit_lines": "open_acc",
        "home_ownership": "home_ownership",
        "loan_purpose": "purpose",
        "default_flag": "loan_status",
    },
    defaults={"credit_history_years": 8},
    percent_columns=("debt_to_income", "interest_rate", "revolving_utilization"),
)

GIVE_ME_SOME_CREDIT_MAPPING = DatasetMapping(
    name="give_me_some_credit",
    columns={
        "annual_income": "MonthlyIncome",
        "debt_to_income": "DebtRatio",
        "delinquency_count": "NumberOfTime30-59DaysPastDueNotWorse",
        "revolving_utilization": "RevolvingUtilizationOfUnsecuredLines",
        "open_credit_lines": "NumberOfOpenCreditLinesAndLoans",
        "default_flag": "SeriousDlqin2yrs",
    },
    defaults={
        "loan_amount": 15000,
        "interest_rate": 0.12,
        "employment_length_years": 5,
        "credit_history_years": 8,
        "home_ownership": "UNKNOWN",
        "loan_purpose": "UNKNOWN",
    },
)

MAPPING_REGISTRY = {
    "canonical": DatasetMapping(name="canonical", columns={}),
    "lending_club": LENDING_CLUB_MAPPING,
    "give_me_some_credit": GIVE_ME_SOME_CREDIT_MAPPING,
}
