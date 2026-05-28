# Implementation Learning Map

This document maps the current implementation to the machine learning, AI engineering, and enterprise modernization concepts used in the project. It is intended as a study guide while building the platform, so each section explains both the concept and how this repository applies it.

## 1. Business Problem Framing

### Concept

An enterprise ML project starts with a business workflow, not a model. The model is only useful if it improves a real decision process, integrates with systems, and creates outputs that business stakeholders can use.

### How This Project Applies It

The platform simulates credit risk modernization for financial institutions. The business workflow is:

1. Receive applicant or loan data.
2. Validate and clean the data.
3. Generate risk features.
4. Predict default probability.
5. Assign a risk tier.
6. Explain the prediction.
7. Log the decision for auditability.
8. Monitor scoring activity and drift.

Key files:

- `PROJECT_SPEC.md`
- `README.md`
- `reports/business_summary.md`

## 2. Target Variable

### Concept

The target variable is the outcome the model learns to predict. In supervised learning, historical records contain input features and the known target outcome.

### How This Project Applies It

The target is:

```text
default_flag
```

This represents whether a borrower defaulted. The model learns patterns that separate default and non-default records.

Key files:

- `src/preprocessing/schema.py`
- `src/training/train_model.py`

## 3. Features

### Concept

Features are the input variables used by the model. In credit risk, features usually describe income, debt, credit history, product terms, and repayment behavior.

### How This Project Applies It

Raw applicant features include:

- annual income
- debt-to-income ratio
- loan amount
- interest rate
- employment length
- credit history length
- delinquency count
- revolving utilization
- open credit lines
- home ownership
- loan purpose

Key files:

- `src/preprocessing/schema.py`
- `src/utils/sample_data.py`

## 4. Data Preprocessing

### Concept

Preprocessing converts messy raw data into consistent data that downstream feature engineering and model training can use. This includes schema checks, type conversion, missing value handling, and range controls.

### How This Project Applies It

The preprocessing layer:

- validates required columns
- converts numeric columns safely
- fills missing numeric values with medians
- standardizes categorical values
- clips unrealistic ranges for selected fields

Key files:

- `src/preprocessing/pipeline.py`
- `tests/test_preprocessing.py`

## 5. Feature Engineering

### Concept

Feature engineering creates model-ready signals from raw data. Strong enterprise ML projects encode business knowledge into features instead of only passing raw columns to a model.

### How This Project Applies It

The feature engineering layer creates:

- `loan_to_income`
- `credit_line_density`
- `delinquency_per_year`
- `high_utilization_flag`
- `thin_file_flag`
- `secured_home_flag`

It also one-hot encodes categorical variables so models can use them numerically.

Key files:

- `src/feature_engineering/features.py`

## 6. One-Hot Encoding

### Concept

One-hot encoding converts categorical text values into binary columns. For example, `home_ownership = RENT` becomes a numeric flag like `home_ownership_RENT`.

### How This Project Applies It

The project uses `pandas.get_dummies()` for categorical fields such as:

- `home_ownership`
- `loan_purpose`

The API aligns incoming one-record payloads to the full training feature list so missing category columns are filled with zero.

Key files:

- `src/feature_engineering/features.py`
- `app/main.py`

## 7. Training Pipeline

### Concept

A training pipeline is a repeatable process that transforms data, trains candidate models, evaluates them, and saves artifacts. It should be reproducible and testable.

### How This Project Applies It

The training workflow:

1. Loads CSV data or generates a development fixture.
2. Builds a training matrix.
3. Splits data into train/test sets.
4. Trains candidate models.
5. Evaluates each model.
6. Selects the best model by ROC-AUC.
7. Saves model and metadata artifacts.

Key files:

- `src/training/train_model.py`
- `tests/test_training.py`

## 8. Candidate Models

### Concept

Enterprise ML teams usually compare a simple baseline against stronger models. This prevents overengineering and helps explain tradeoffs.

### How This Project Applies It

The project currently trains:

- Logistic Regression: interpretable baseline.
- Random Forest: nonlinear tree ensemble.
- XGBoost: optional gradient boosting model for tabular risk modeling.

Key files:

- `src/training/train_model.py`
- `requirements.txt`

## 9. Class Imbalance

### Concept

Credit defaults are usually less common than non-defaults. Class imbalance can cause a model to ignore the minority default class unless handled carefully.

### How This Project Applies It

The project uses:

- `class_weight="balanced"` for Logistic Regression and Random Forest.
- `scale_pos_weight` for XGBoost.

This helps the model pay more attention to default cases.

Key file:

- `src/training/train_model.py`

## 10. Model Evaluation Metrics

### Concept

Different metrics answer different business questions:

- ROC-AUC: how well the model ranks risk.
- Precision: when the model flags risk, how often it is right.
- Recall: how many actual defaults the model catches.
- F1: balance between precision and recall.
- Confusion matrix: counts true/false positives and negatives.

### How This Project Applies It

The evaluation layer calculates all required metrics from the project specification.

Key files:

- `src/evaluation/metrics.py`
- `artifacts/models/model_metrics.json`

## 11. Threshold Optimization

### Concept

ML classifiers output probabilities. A threshold converts those probabilities into operational decisions. For example, a borrower with default probability above 0.45 may require manual review.

### How This Project Applies It

The project searches thresholds from 0.20 to 0.80 and selects the threshold with the best F1 score. The selected threshold is saved in model metadata and returned by the API.

Key files:

- `src/evaluation/metrics.py`
- `src/training/train_model.py`
- `app/main.py`

## 12. Model Artifacts

### Concept

Model artifacts are saved outputs from training that allow the model to be reused later. Artifacts usually include the trained model, feature schema, metrics, and metadata.

### How This Project Applies It

Training writes:

- `credit_risk_model.joblib`
- `model_metadata.json`
- `model_metrics.json`
- `feature_schema.json`
- `global_explainability.json`

These files are generated runtime artifacts and are intentionally ignored by Git.

Key directory:

- `artifacts/models/`

## 13. Explainable AI

### Concept

Explainable AI helps stakeholders understand why a model made a prediction. This is especially important in finance because risk decisions need governance, transparency, and auditability.

### How This Project Applies It

The project supports:

- local explanations for individual applicants
- business-readable reason codes
- global feature importance artifacts
- graceful fallback when SHAP is unavailable

Key files:

- `src/explainability/shap_explainer.py`
- `tests/test_explainability.py`

## 14. SHAP

### Concept

SHAP estimates how much each feature contributes to a model prediction. It is widely used for model interpretation and model risk review.

### How This Project Applies It

The API attempts to generate local SHAP-style explanations for each prediction. If SHAP cannot run in a specific environment, the system falls back to model-native coefficients or feature importance.

Key file:

- `src/explainability/shap_explainer.py`

## 14.1 Model Governance

### Concept

Model governance is the set of controls, documents, and review processes that make ML systems auditable and appropriate for their intended use. In financial services, governance typically covers intended use, limitations, data quality, model evaluation, explainability, monitoring, and approval requirements.

### How This Project Applies It

The project now includes a model card, governance checklist, and generated governance report. These documents clarify that the platform is a modernization simulation, not a regulated credit approval engine.

Key files:

- `docs/MODEL_CARD.md`
- `docs/GOVERNANCE_CHECKLIST.md`
- `src/evaluation/governance_report.py`
- `src/evaluation/governance_cli.py`
- `tests/test_governance_report.py`

## 15. Reason Codes

### Concept

Reason codes translate technical model drivers into business language. They help underwriters, compliance teams, and business stakeholders understand the main drivers behind a score.

### How This Project Applies It

Examples include:

- Elevated debt-to-income ratio
- High revolving credit utilization
- Recent or repeated delinquency history
- Limited credit history

Key file:

- `src/explainability/shap_explainer.py`

## 16. FastAPI Serving Layer

### Concept

An ML model usually needs to be served through an API so other systems can call it. FastAPI is a modern Python framework for building typed REST APIs.

### How This Project Applies It

The API exposes:

- `GET /health`
- `POST /predict`
- `POST /batch_predict`
- `GET /metrics`

Prediction responses include probability, tier, model version, threshold, reason codes, top features, and timestamp.

Key files:

- `app/main.py`
- `tests/test_api.py`

## 17. Pydantic Request Validation

### Concept

Pydantic validates API request payloads before they reach business logic. This prevents invalid inputs from silently entering the model.

### How This Project Applies It

The `ApplicantPayload` model validates fields such as:

- positive income
- non-negative debt-to-income ratio
- valid interest rate range
- non-negative credit history and delinquency counts

Key file:

- `app/main.py`

## 18. Prediction Logging

### Concept

Prediction logging creates an audit trail of model outputs. In enterprise systems, this supports monitoring, debugging, compliance, and model governance.

### How This Project Applies It

The API writes JSONL prediction logs containing:

- risk probability
- risk tier
- model version
- request inputs
- timestamp

Key files:

- `src/monitoring/logging.py`
- `artifacts/logs/predictions.jsonl`

## 19. Monitoring

### Concept

Monitoring checks whether a model and service are behaving as expected after deployment. It can include API health, prediction volume, prediction distribution, model performance, and data drift.

### How This Project Applies It

The current implementation includes:

- API counters
- prediction score distribution summaries
- prediction logs
- `/metrics` endpoint
- drift report generation using Population Stability Index

Key files:

- `src/monitoring/metrics.py`
- `src/monitoring/drift.py`
- `src/monitoring/drift_cli.py`
- `app/main.py`

## 20. Data Drift

### Concept

Data drift happens when production input data changes compared with training data. Drift can make model performance worse over time.

### How This Project Applies It

The project includes Population Stability Index utilities and a persisted drift report generator that compares reference and current feature distributions.

Key files:

- `src/monitoring/drift.py`
- `src/monitoring/drift_cli.py`
- `docs/MONITORING_DESIGN.md`

## 21. Streamlit Dashboard

### Concept

Dashboards help stakeholders inspect model behavior, scoring activity, and risk trends without reading code.

### How This Project Applies It

The dashboard currently displays:

- model metrics
- prediction activity
- risk tier distribution
- global explainability chart

Key file:

- `dashboard/streamlit_app.py`

## 22. Docker

### Concept

Docker packages an application and its dependencies so it runs consistently across environments.

### How This Project Applies It

The project includes:

- `Dockerfile` for API packaging
- `docker-compose.yml` for running API and dashboard together

Key files:

- `Dockerfile`
- `docker-compose.yml`

## 23. CI/CD

### Concept

CI/CD automates validation when code changes. CI commonly runs tests, syntax checks, and build checks before code is merged or deployed.

### How This Project Applies It

GitHub Actions currently:

- installs dependencies
- compiles Python modules
- runs pytest

Key file:

- `.github/workflows/ci.yml`

## 24. Testing

### Concept

Tests verify that important behaviors still work as the system changes. In ML systems, tests should cover data processing, model training, API behavior, and explainability utilities.

### How This Project Applies It

Current tests cover:

- preprocessing behavior
- training artifact creation
- API health and prediction endpoints
- explainability outputs
- data ingestion, data quality, monitoring, batch scoring, and API hardening

Key directory:

- `tests/`

## 25. SQL And Data Contracts

### Concept

Enterprise systems often define data schemas explicitly. SQL schemas and data contracts make upstream/downstream expectations clear.

### How This Project Applies It

The repository includes SQL tables for:

- credit applications
- prediction audit logs

Key file:

- `sql/schema.sql`

## 26. Dataset Mapping

### Concept

Real datasets rarely arrive in the exact format a model expects. Dataset mapping translates source-specific columns and business definitions into a canonical schema used by the rest of the platform.

### How This Project Applies It

The ingestion layer supports named mappings for:

- canonical platform data
- LendingClub-style data
- Give Me Some Credit-style data

The training command can now accept a mapping profile, and a separate CLI can convert source CSVs into the canonical schema.

Key files:

- `docs/DATA_CONTRACT.md`
- `src/data_ingestion/mappings.py`
- `src/data_ingestion/loader.py`
- `src/data_ingestion/cli.py`
- `tests/test_data_ingestion.py`

## 27. Data Quality Reporting

### Concept

Data quality reporting verifies whether source data is complete, valid, and usable before model training or scoring. It is a core enterprise ML control because bad input data can create unreliable model outputs.

### How This Project Applies It

The project now generates JSON data quality reports with:

- row and column counts
- missing column checks
- missing value summary
- numeric range validation
- categorical distributions
- target balance summary

Training automatically writes a report, and a standalone CLI can generate one for mapped source datasets.

Key files:

- `docs/DATA_QUALITY_REPORTING.md`
- `src/data_ingestion/quality.py`
- `src/data_ingestion/quality_cli.py`
- `tests/test_data_quality.py`

## 28. Batch Scoring

### Concept

Batch scoring applies a trained model to many records at once. Enterprises use batch scoring for portfolio review, back-office underwriting queues, periodic risk monitoring, and pre-deployment validation.

### How This Project Applies It

The project now has a reusable scoring service shared by FastAPI and the batch CLI. The CLI loads a source CSV, maps it to the canonical schema, scores each record, writes a prediction CSV, and logs prediction events for auditability.

Key files:

- `docs/BATCH_SCORING_WORKFLOW.md`
- `src/scoring/service.py`
- `src/scoring/batch_score.py`
- `tests/test_batch_scoring.py`

## 29. API Hardening

### Concept

API hardening makes a service safer and more predictable for downstream systems. It includes request validation, structured errors, request tracing, input size limits, and health checks that expose dependency readiness.

### How This Project Applies It

The FastAPI service now includes:

- request ID propagation through `X-Request-ID`
- structured validation error responses
- category validation for applicant fields
- batch size limits for `/batch_predict`
- artifact-level health reporting

Key files:

- `docs/API_HARDENING.md`
- `app/main.py`
- `tests/test_api.py`

## 30. Current Gaps To Learn Next

The next learning and implementation areas are:

1. Dashboard improvements for portfolio risk exploration.
2. Deployment documentation for cloud environments.

These map directly to the remaining work in `PROJECT_SPEC.md`.
