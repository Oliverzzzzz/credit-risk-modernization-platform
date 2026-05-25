# Data Contract

This document defines the canonical input schema for the credit risk modernization platform and explains how external public datasets should be mapped into that schema. The goal is to keep data ingestion realistic while avoiding dataset-specific logic inside the training and scoring pipelines.

## Canonical Training Schema

The platform expects one row per applicant or loan record.

| Column | Type | Required | Description |
|---|---|---:|---|
| `annual_income` | numeric | yes | Borrower annual income in currency units. |
| `debt_to_income` | numeric | yes | Debt-to-income ratio as a decimal, such as `0.32`. |
| `loan_amount` | numeric | yes | Requested or originated loan amount. |
| `interest_rate` | numeric | yes | Loan interest rate as a decimal, such as `0.1199`. |
| `employment_length_years` | numeric | yes | Approximate borrower employment history in years. |
| `credit_history_years` | numeric | yes | Length of observed credit history in years. |
| `delinquency_count` | numeric | yes | Count of delinquency events in the observation window. |
| `revolving_utilization` | numeric | yes | Revolving credit utilization as a decimal. |
| `open_credit_lines` | numeric | yes | Count of open credit lines. |
| `home_ownership` | categorical | yes | Borrower home ownership status. |
| `loan_purpose` | categorical | yes | Borrower loan purpose. |
| `default_flag` | integer | training only | `1` for default or severe delinquency, `0` otherwise. |

## Supported Source Dataset Strategy

The platform is designed for realistic public financial datasets, including:

- LendingClub loan performance data.
- Give Me Some Credit.
- Home Credit Default Risk.

These datasets do not use identical column names or target definitions. The ingestion layer should therefore map source-specific columns into the canonical schema before preprocessing, feature engineering, and training.

## Mapping Rules

### LendingClub-Style Data

Common source fields can be mapped as follows:

| Canonical Column | Common Source Column |
|---|---|
| `annual_income` | `annual_inc` |
| `debt_to_income` | `dti` |
| `loan_amount` | `loan_amnt` |
| `interest_rate` | `int_rate` |
| `employment_length_years` | `emp_length` |
| `credit_history_years` | `earliest_cr_line` plus issue date, or a prepared numeric field |
| `delinquency_count` | `delinq_2yrs` |
| `revolving_utilization` | `revol_util` |
| `open_credit_lines` | `open_acc` |
| `home_ownership` | `home_ownership` |
| `loan_purpose` | `purpose` |
| `default_flag` | derived from `loan_status` |

For `loan_status`, statuses such as `Charged Off`, `Default`, and severe late statuses should map to `1`; fully paid/current statuses should map to `0` depending on the modeling window.

### Give Me Some Credit-Style Data

Common source fields can be mapped as follows:

| Canonical Column | Common Source Column |
|---|---|
| `annual_income` | `MonthlyIncome` multiplied by `12` |
| `debt_to_income` | `DebtRatio` |
| `loan_amount` | not directly available; use a proxy or exclude unless enriched |
| `interest_rate` | not directly available; use a configured proxy if needed |
| `employment_length_years` | not directly available; use a configured proxy if needed |
| `credit_history_years` | not directly available; use a configured proxy if needed |
| `delinquency_count` | `NumberOfTime30-59DaysPastDueNotWorse` plus severe delinquency counts |
| `revolving_utilization` | `RevolvingUtilizationOfUnsecuredLines` |
| `open_credit_lines` | `NumberOfOpenCreditLinesAndLoans` |
| `home_ownership` | not directly available; use `UNKNOWN` |
| `loan_purpose` | not directly available; use `UNKNOWN` |
| `default_flag` | `SeriousDlqin2yrs` |

This dataset is useful for credit behavior modeling, but it requires explicit assumptions because it does not contain all origination fields.

### Home Credit-Style Data

Home Credit contains multiple relational tables. A production ingestion workflow would join applicant, bureau, previous application, and repayment tables before mapping to the canonical schema. This repository should treat Home Credit ingestion as a future enrichment path rather than a single flat CSV assumption.

## Development Fixture

The repository includes a synthetic data generator for local development and CI. This fixture is used only to validate platform behavior before a real public dataset is connected. It should not be represented as production training data.

Key file:

```text
src/utils/sample_data.py
```

## Ingestion Expectations

The ingestion layer should:

1. Read a source CSV.
2. Apply a named dataset mapping.
3. Standardize units and formats.
4. Return the canonical schema.
5. Validate that all required fields exist before training.

The preprocessing layer remains responsible for type conversion, missing values, range clipping, and categorical normalization.
