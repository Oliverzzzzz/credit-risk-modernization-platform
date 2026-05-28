# Deployment Guide

This guide describes local and cloud-oriented deployment paths for the credit risk modernization platform.

## Local Development

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Train local artifacts:

```bash
python -m src.training.train_model --generate-sample
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Run the dashboard:

```bash
streamlit run dashboard/streamlit_app.py
```

## Docker Deployment

Build the image:

```bash
docker build -t credit-risk-platform .
```

Run the API:

```bash
docker run -p 8000:8000 credit-risk-platform
```

Run API and dashboard:

```bash
docker compose up --build
```

## Environment And Artifact Expectations

The platform expects these runtime artifact directories:

```text
artifacts/models/
artifacts/logs/
artifacts/reports/
data/raw/
data/processed/
```

Model artifacts:

```text
artifacts/models/credit_risk_model.joblib
artifacts/models/model_metadata.json
artifacts/models/model_metrics.json
artifacts/models/feature_schema.json
artifacts/models/global_explainability.json
```

## Cloud Deployment Roadmap

Recommended cloud architecture:

- API container on AWS ECS, Azure Container Apps, Google Cloud Run, or Kubernetes.
- Dashboard container as an internal analytics app.
- Object storage for model and report artifacts.
- Managed PostgreSQL for prediction audit logs.
- GitHub Actions for CI and deployment promotion.
- Centralized logging and metrics through cloud observability tooling.

## Deployment Controls Before Production

Before production use, add:

- authentication and authorization
- secrets management
- model registry
- artifact versioning
- database-backed audit logs
- fairness and bias review
- delayed-label model performance monitoring
- alerting for drift and API errors

## Current Project Position

This project is deployment-ready for local Docker demonstration. It is not production-ready for regulated financial decisioning without additional controls.
