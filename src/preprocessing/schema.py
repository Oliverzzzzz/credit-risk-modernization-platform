NUMERIC_COLUMNS = [
    "annual_income",
    "debt_to_income",
    "loan_amount",
    "interest_rate",
    "employment_length_years",
    "credit_history_years",
    "delinquency_count",
    "revolving_utilization",
    "open_credit_lines",
]

CATEGORICAL_COLUMNS = ["home_ownership", "loan_purpose"]

TARGET_COLUMN = "default_flag"

REQUIRED_COLUMNS = NUMERIC_COLUMNS + CATEGORICAL_COLUMNS

TRAINING_COLUMNS = REQUIRED_COLUMNS + [TARGET_COLUMN]
