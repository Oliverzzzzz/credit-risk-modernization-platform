import numpy as np
import pandas as pd


def generate_credit_sample(rows: int = 1200, random_state: int = 42) -> pd.DataFrame:
    """Generate a business-shaped development fixture for local runs and CI."""
    rng = np.random.default_rng(random_state)
    annual_income = rng.lognormal(mean=11.0, sigma=0.45, size=rows).clip(22000, 260000)
    loan_amount = rng.normal(18000, 7500, size=rows).clip(1500, 60000)
    debt_to_income = rng.beta(2.2, 5.0, size=rows).clip(0.02, 0.92)
    interest_rate = rng.normal(0.13, 0.045, size=rows).clip(0.035, 0.34)
    employment_length_years = rng.integers(0, 21, size=rows)
    credit_history_years = rng.integers(1, 31, size=rows)
    delinquency_count = rng.poisson(0.45, size=rows).clip(0, 8)
    revolving_utilization = rng.beta(2.0, 3.0, size=rows).clip(0.01, 1.0)
    open_credit_lines = rng.integers(1, 18, size=rows)
    home_ownership = rng.choice(["RENT", "MORTGAGE", "OWN"], size=rows, p=[0.42, 0.45, 0.13])
    loan_purpose = rng.choice(
        ["debt_consolidation", "home_improvement", "small_business", "medical", "major_purchase"],
        size=rows,
        p=[0.48, 0.18, 0.12, 0.10, 0.12],
    )

    logit = (
        -3.1
        + 3.2 * debt_to_income
        + 2.1 * revolving_utilization
        + 0.18 * delinquency_count
        + 4.0 * interest_rate
        + 0.000015 * loan_amount
        - 0.000012 * annual_income
        - 0.025 * employment_length_years
        - 0.018 * credit_history_years
        + np.where(home_ownership == "RENT", 0.22, 0.0)
        + np.where(loan_purpose == "small_business", 0.28, 0.0)
    )
    probability = 1 / (1 + np.exp(-logit))
    default_flag = rng.binomial(1, probability)

    return pd.DataFrame(
        {
            "annual_income": annual_income.round(2),
            "debt_to_income": debt_to_income.round(4),
            "loan_amount": loan_amount.round(2),
            "interest_rate": interest_rate.round(4),
            "employment_length_years": employment_length_years,
            "credit_history_years": credit_history_years,
            "delinquency_count": delinquency_count,
            "revolving_utilization": revolving_utilization.round(4),
            "open_credit_lines": open_credit_lines,
            "home_ownership": home_ownership,
            "loan_purpose": loan_purpose,
            "default_flag": default_flag,
        }
    )
