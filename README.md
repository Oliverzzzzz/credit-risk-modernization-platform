# Credit Risk Modernization Platform

Enterprise-style AI/ML platform for modernizing credit risk workflows with machine learning, explainable AI, FastAPI services, monitoring, Docker, and CI/CD.

This project is framed as a realistic financial services modernization initiative: a legacy credit assessment workflow is refactored into governed data pipelines, reusable feature engineering, explainable model scoring, API-based decision support, and operational monitoring.

## Architecture

```text
Raw applicant/loan data
        |
        v
Preprocessing and schema validation
        |
        v
Feature engineering pipeline
        |
        v
Model training and evaluation
        |
        +--> SHAP explainability artifacts
        |
        v
FastAPI risk scoring service
        |
        +--> Prediction logs and API metrics
        |
        v
Streamlit portfolio dashboard
```

## What This Demonstrates

- Modular Python architecture for maintainable ML systems.
- SQL-friendly data and audit design.
- Baseline and tree-based credit risk model training.
- SHAP-based explainability and business reason codes.
- Real-time and batch prediction APIs.
- Lightweight monitoring for prediction logging and drift checks.
- Dockerized local deployment.
- GitHub Actions CI for tests and import validation.

## Repository Structure

```text
credit-risk-modernization-platform/
├── app/                      # FastAPI application
├── dashboard/                # Streamlit dashboard
├── data/                     # Raw and processed data placeholders
├── src/                      # Production ML and platform modules
├── tests/                    # pytest suite
├── reports/                  # Enterprise documentation
├── sql/                      # SQL schema definitions
├── artifacts/                # Runtime model and log artifacts
├── Dockerfile
├── docker-compose.yml
├── PROJECT_SPEC.md
└── requirements.txt
```

## Enterprise Documentation

- `docs/ARCHITECTURE_DIAGRAMS.md`
- `docs/DEPLOYMENT_GUIDE.md`
- `docs/DEPLOYMENT_CHECKLIST.md`
- `docs/CICD_WORKFLOW.md`
- `docs/MODEL_CARD.md`
- `docs/GOVERNANCE_CHECKLIST.md`
- `docs/IMPLEMENTATION_LEARNING_MAP.md`

## Data Strategy

The platform is designed for realistic public financial datasets such as Home Credit Default Risk, LendingClub, or Give Me Some Credit. For local development and CI, the code can generate a synthetic credit-like fixture with business-oriented fields. That fixture exists only to prove the platform workflow before a real dataset is connected.

Dataset-specific CSVs should be mapped into the platform's canonical schema before training. The canonical data contract is documented in `docs/DATA_CONTRACT.md`.

Expected target column:

```text
default_flag
```

Expected applicant fields include income, debt, loan amount, interest rate, employment length, credit history length, delinquency count, revolving utilization, open credit lines, and home ownership.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.training.train_model --generate-sample
uvicorn app.main:app --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Run the dashboard:

```bash
streamlit run dashboard/streamlit_app.py
```

The dashboard includes portfolio, model performance, explainability, monitoring, and governance review tabs.

## API Examples

The API returns an `X-Request-ID` header for traceability. Clients can provide their own request ID:

Health check:

```bash
curl -H "X-Request-ID: demo-health-check" http://127.0.0.1:8000/health
```

Single prediction:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: demo-score-001" \
  -d '{
    "annual_income": 85000,
    "debt_to_income": 0.28,
    "loan_amount": 18000,
    "interest_rate": 0.11,
    "employment_length_years": 6,
    "credit_history_years": 9,
    "delinquency_count": 0,
    "revolving_utilization": 0.34,
    "open_credit_lines": 7,
    "home_ownership": "MORTGAGE",
    "loan_purpose": "debt_consolidation"
  }'
```

The `/batch_predict` API accepts up to 100 applicants per request. Larger portfolio scoring jobs should use the batch scoring CLI.

Validation errors use a structured response with an error code, message, request ID, and validation details.

## Model Training

```bash
python -m src.training.train_model --input data/raw/credit_applications.csv
```

For a supported source dataset, pass the mapping profile:

```bash
python -m src.training.train_model \
  --input data/raw/lending_club_sample.csv \
  --mapping lending_club
```

If no input file is available:

```bash
python -m src.training.train_model --generate-sample
```

To map a source CSV into the canonical schema without training:

```bash
python -m src.data_ingestion.cli \
  --input data/raw/lending_club_sample.csv \
  --output data/processed/canonical_credit_applications.csv \
  --mapping lending_club
```

To generate a standalone data quality report:

```bash
python -m src.data_ingestion.quality_cli \
  --input data/raw/lending_club_sample.csv \
  --mapping lending_club \
  --output artifacts/reports/data_quality_report.json
```

## Batch Scoring

Batch scoring simulates portfolio review workflows where many applicant records are scored together:

```bash
python -m src.scoring.batch_score \
  --input data/raw/applicants.csv \
  --output data/processed/batch_predictions.csv \
  --mapping canonical
```

For faster scoring without reason-code generation:

```bash
python -m src.scoring.batch_score \
  --input data/raw/applicants.csv \
  --output data/processed/batch_predictions.csv \
  --mapping canonical \
  --no-explanations
```

Training writes artifacts to `artifacts/models/`, including:

- `credit_risk_model.joblib`
- `model_metadata.json`
- `model_metrics.json`
- `feature_schema.json`
- `global_explainability.json`

Training also writes a data quality report to:

```text
artifacts/reports/data_quality_report.json
```

Generate a model governance report from training artifacts:

```bash
python -m src.evaluation.governance_cli \
  --output artifacts/reports/model_governance_report.json
```

## Explainability

The explainability layer uses SHAP where possible and falls back to model-native importance when needed. API prediction responses include reason codes such as elevated debt-to-income, high revolving utilization, adverse delinquency history, or limited credit history.

Governance outputs are intended to support:

- Local borrower-level explanations.
- Global feature importance.
- Persisted model review artifacts.
- Model card and governance review documentation.
- Model risk review.
- Business stakeholder interpretation.

## Monitoring

Runtime monitoring includes:

- JSONL prediction logs in `artifacts/logs/predictions.jsonl`.
- API counters and score distribution summaries exposed at `/metrics`.
- Drift comparison utilities in `src/monitoring/drift.py`.
- PSI drift report generation in `artifacts/reports/drift_report.json`.

The monitoring implementation is intentionally lightweight, but it mirrors the operational concerns an enterprise team would address before production deployment.

Generate a drift report from reference and current datasets:

```bash
python -m src.monitoring.drift_cli \
  --reference data/processed/reference_features.csv \
  --current data/processed/current_features.csv \
  --output artifacts/reports/drift_report.json
```

## Docker

Build and run the API:

```bash
docker build -t credit-risk-platform .
docker run -p 8000:8000 credit-risk-platform
```

Run API and dashboard together:

```bash
docker compose up --build
```

## Testing and CI

Run tests locally:

```bash
pytest
```

GitHub Actions runs import checks and tests on push and pull request events.

## Deployment Roadmap

Recommended enterprise deployment path:

- Containerize the API and dashboard.
- Store model artifacts in object storage.
- Persist audit logs in PostgreSQL.
- Add model registry and approval workflows.
- Add Prometheus/Grafana or managed observability.
- Add scheduled retraining and drift review workflows.
- Deploy to AWS ECS, Azure Container Apps, Google Cloud Run, or Kubernetes.

See `docs/DEPLOYMENT_GUIDE.md` and `docs/ARCHITECTURE_DIAGRAMS.md` for deployment and architecture details.

## Resume-Aligned Summary

Designed and developed an AI-driven enterprise credit risk modernization platform using Python, FastAPI, SQL-style pipelines, explainable ML, Docker, and GitHub Actions to simulate how financial institutions modernize risk assessment workflows.
