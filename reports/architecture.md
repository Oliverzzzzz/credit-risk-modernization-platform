# Architecture Overview

The platform separates data preparation, feature engineering, model training, explainability, serving, and monitoring into independent modules. This mirrors enterprise AI delivery patterns where batch model development and real-time decision services are maintained by different teams but share governed artifacts.

## Logical Components

- Data layer: CSV and SQL-compatible schemas for applicant data and audit logs.
- ML layer: preprocessing, feature engineering, training, evaluation, and artifact persistence.
- Explainability layer: SHAP and fallback model importance for local reason codes.
- Service layer: FastAPI endpoints for health, prediction, batch prediction, and metrics.
- Monitoring layer: structured prediction logs and lightweight counters.
- Presentation layer: Streamlit dashboard for model and portfolio review.

## Production Extension Points

- Replace local artifacts with a model registry.
- Replace JSONL logs with PostgreSQL or centralized logging.
- Add data quality checks before training and scoring.
- Add role-based access control around scoring endpoints.
- Add CI/CD promotion environments for dev, staging, and production.
