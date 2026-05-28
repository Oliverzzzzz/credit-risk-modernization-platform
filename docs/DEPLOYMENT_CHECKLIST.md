# Deployment Checklist

## Local Demonstration

- [x] Dependencies install from `requirements.txt`.
- [x] Model training command is documented.
- [x] API can run with Uvicorn.
- [x] Dashboard can run with Streamlit.
- [x] Dockerfile is available.
- [x] docker-compose workflow is available.
- [x] Tests pass locally and in CI.

## Container Readiness

- [x] API container starts with Uvicorn.
- [x] Model artifacts are generated during image build.
- [x] Runtime artifact volumes are mounted in docker-compose.
- [ ] Image vulnerability scanning configured.
- [ ] Separate production image profile configured.

## Cloud Readiness

- [ ] Container registry configured.
- [ ] Managed database configured for audit logs.
- [ ] Object storage configured for model artifacts.
- [ ] Secrets management configured.
- [ ] Authentication and authorization configured.
- [ ] Centralized logging configured.
- [ ] Monitoring and alerting configured.
- [ ] Deployment promotion workflow configured.

## Model Governance Readiness

- [x] Model card documented.
- [x] Governance checklist documented.
- [x] Data quality reports implemented.
- [x] Drift reports implemented.
- [x] Explainability artifacts implemented.
- [ ] Fairness analysis implemented.
- [ ] Model registry approval implemented.
- [ ] Delayed-label monitoring implemented.
