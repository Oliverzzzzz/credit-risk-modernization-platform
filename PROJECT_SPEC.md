# AI-Driven Enterprise Credit Risk Modernization Platform

## 1. Project Overview

This repository simulates an enterprise AI modernization initiative for financial institutions that want to modernize legacy credit risk workflows. The platform combines SQL-style data pipelines, machine learning, explainable AI, REST APIs, monitoring, Docker deployment, CI/CD, and consulting-grade documentation.

The goal is not to create a notebook-only credit model. The goal is to demonstrate how an enterprise AI team would design a maintainable risk analytics service that can ingest applicant data, transform it into governed features, score default risk, explain model decisions, expose predictions through APIs, and monitor operational behavior.

Core capabilities:

- Ingest applicant and loan data from CSV or SQL-backed sources.
- Validate schemas and clean input data before modeling.
- Generate business-relevant credit risk features.
- Train baseline and tree-based credit risk models.
- Evaluate model performance with technical and business metrics.
- Generate local and global explainability outputs using SHAP.
- Serve real-time and batch predictions through FastAPI.
- Log predictions and service events for auditability.
- Provide a Streamlit dashboard for portfolio risk exploration.
- Package the platform with Docker and validate changes with GitHub Actions.

## 2. Business Goals

Financial institutions often operate credit workflows that are fragmented across legacy systems, spreadsheet-based review processes, manual policy checks, and black-box scoring outputs. These workflows can slow down underwriting decisions, limit transparency, and make governance difficult.

This platform is designed around the following business outcomes:

- Improve decision speed by exposing risk scores through APIs.
- Improve transparency through SHAP explanations and reason codes.
- Improve consistency by centralizing preprocessing and feature engineering logic.
- Improve auditability by logging inputs, scores, model versions, and timestamps.
- Improve deployment reliability through repeatable Docker and CI/CD workflows.
- Improve executive visibility through portfolio-level dashboards and reports.

## 3. Target Users

The system is framed for:

- Credit risk modernization teams.
- Enterprise AI and ML engineering teams.
- Technology consulting teams.
- Model risk governance and compliance stakeholders.
- Digital transformation teams supporting financial institutions.

## 4. Business Workflow

The target workflow is:

1. Applicant or loan data enters the platform from a source system.
2. The preprocessing layer validates required fields, handles missing values, and standardizes records.
3. The feature engineering layer produces risk-relevant derived variables.
4. The trained model generates a probability of default.
5. The decision layer maps the probability to a Low, Medium, or High risk tier.
6. The explainability layer produces feature-level drivers and reason codes.
7. The API returns a prediction response and writes an audit log.
8. Monitoring components track drift signals, prediction distributions, and service health.
9. Documentation and reports communicate model behavior, risks, and deployment expectations.

## 5. Functional Requirements

### Risk Scoring

- Generate borrower default probabilities.
- Support real-time single applicant scoring.
- Support batch scoring for portfolio reviews.
- Return model version and timestamp with every prediction.

### Risk Tiering

- Low Risk: low estimated probability of default.
- Medium Risk: moderate estimated probability of default.
- High Risk: elevated estimated probability of default.
- Thresholds must be configurable and documented.

### Explainability

- Generate global feature importance.
- Generate local borrower-level explanations.
- Convert top adverse SHAP drivers into business-readable reason codes.
- Store explanation artifacts for model governance.

### Auditability

- Log prediction request metadata.
- Log model version and risk outputs.
- Preserve feature inputs required to reproduce scores.
- Write structured logs to `artifacts/logs/`.

### Monitoring

- Track API health and prediction volume.
- Track prediction score distributions.
- Track simple drift statistics between reference and current datasets.
- Provide `/metrics` output for operational checks.

## 6. Technical Architecture

### Application Layers

- `src/preprocessing`: schema validation, cleaning, and type normalization.
- `src/feature_engineering`: business feature generation.
- `src/training`: model training, model selection, and artifact persistence.
- `src/evaluation`: model metrics and reporting utilities.
- `src/explainability`: SHAP explainers, feature importance, and reason codes.
- `src/monitoring`: prediction logging, API metrics, and drift checks.
- `src/utils`: configuration, data loading, paths, and sample data generation.
- `app`: FastAPI service layer.
- `dashboard`: Streamlit analytics dashboard.
- `reports`: consulting-style architecture and model documentation.
- `sql`: SQL schema definitions for operational and feature stores.

### API Architecture

The FastAPI service exposes:

- `GET /health`: service, model, and artifact health.
- `POST /predict`: single applicant prediction with explanation.
- `POST /batch_predict`: batch applicant scoring.
- `GET /metrics`: lightweight operational metrics.

Responses must include:

- Risk probability.
- Risk tier.
- Model version.
- Timestamp.
- Optional reason codes.

### Data Architecture

The platform is designed to work with realistic credit datasets such as:

- Home Credit Default Risk.
- LendingClub loan performance data.
- Give Me Some Credit.

The codebase includes a governed synthetic sample generator only to support local development and CI before a public dataset is connected. The README must clearly frame this sample data as a development fixture, not as a substitute for enterprise training data.

### ML Architecture

Model candidates:

- Logistic Regression baseline.
- Random Forest classifier.
- XGBoost classifier when installed and selected.

Required evaluation metrics:

- ROC-AUC.
- Precision.
- Recall.
- F1.
- Confusion matrix.

The training process must support:

- Reproducible train/test split.
- Class imbalance handling through model weights.
- Threshold-based business decisions.
- Saved artifacts for model, feature list, metrics, and thresholds.

### Explainability Architecture

The explainability layer must support:

- SHAP explanations for model governance.
- Global feature importance.
- Local feature contribution explanations.
- Reason code mapping for adverse risk drivers.

When SHAP cannot explain a model in the runtime environment, the layer should degrade gracefully to model feature importance or coefficient-based explanations.

### Monitoring Architecture

Monitoring is intentionally lightweight but enterprise-framed:

- Structured prediction logging in JSONL.
- In-memory API counters for local operation.
- Drift summary generated from reference/current feature datasets.
- Metrics endpoint for service-level checks.

Future production enhancements:

- Prometheus/Grafana integration.
- Evidently or WhyLabs drift reports.
- Model registry integration.
- Centralized log aggregation.
- Batch data quality SLAs.

## 7. MLOps Requirements

The repository must include:

- Dockerfile for API packaging.
- docker-compose.yml for local API and dashboard workflows.
- GitHub Actions CI for linting/import checks and tests.
- Test coverage for preprocessing, training, explainability, and API behavior.
- Versioned artifacts in `artifacts/models/` and runtime logs in `artifacts/logs/`.
- Clear setup and deployment documentation.

CI expectations:

- Install dependencies.
- Run tests with `pytest`.
- Run a syntax/import validation step.
- Avoid committing generated model binaries unless explicitly needed.

## 8. Documentation Requirements

Documentation must include:

- Business context.
- Architecture overview.
- Setup instructions.
- Data expectations.
- Training workflow.
- API usage examples.
- Explainability overview.
- Monitoring overview.
- Docker usage.
- CI/CD workflow.
- Deployment roadmap.

## 9. Deployment Goals

Local deployment:

- Run API with Uvicorn.
- Run dashboard with Streamlit.
- Run services with Docker Compose.

Cloud deployment targets:

- Containerized API on AWS ECS, Azure Container Apps, Google Cloud Run, or Kubernetes.
- Managed PostgreSQL for operational data and audit logs.
- Object storage for model and explanation artifacts.
- CI/CD release workflow from GitHub Actions.

## 10. Non-Goals

This repository does not claim to be a regulated production credit approval engine. It is a realistic modernization simulation intended for portfolio, interview, and architecture demonstration purposes. It avoids fake production claims while showing how a consulting-grade system would be structured and reasoned about.

## 11. Initial Implementation Scope

The initial build includes:

- Full production-style folder structure.
- `requirements.txt`.
- README draft.
- Preprocessing pipeline.
- Feature engineering pipeline.
- Baseline ML training pipeline.
- FastAPI backend.
- SHAP explainability layer.
- Monitoring utilities.
- Streamlit dashboard.
- Docker setup.
- GitHub Actions CI/CD workflow.
- Tests and architecture documentation.
