# Model Governance Checklist

This checklist summarizes controls expected in an enterprise credit risk modernization workflow.

## Data Controls

- [x] Canonical data contract documented.
- [x] Dataset mapping layer implemented.
- [x] Data quality report generated.
- [x] Missing value checks included.
- [x] Numeric range checks included.
- [x] Target balance summary included.
- [ ] Fairness and protected-class review implemented.
- [ ] Source dataset lineage and approval workflow implemented.

## Model Controls

- [x] Multiple model candidates compared.
- [x] Holdout evaluation metrics generated.
- [x] Threshold policy stored in metadata.
- [x] Model metadata artifact generated.
- [x] Feature schema artifact generated.
- [ ] Model registry integration implemented.
- [ ] Formal approval gate implemented.

## Explainability Controls

- [x] Local reason codes implemented.
- [x] Global feature importance artifact generated.
- [x] Explainability fallback implemented.
- [ ] SHAP plots exported as image artifacts.
- [ ] Fairness explainability review implemented.

## Monitoring Controls

- [x] Prediction logging implemented.
- [x] API metrics endpoint implemented.
- [x] Score distribution metrics implemented.
- [x] PSI drift report implemented.
- [ ] Delayed-label performance monitoring implemented.
- [ ] Automated alerts implemented.

## API And Deployment Controls

- [x] API request validation implemented.
- [x] Structured error responses implemented.
- [x] Request ID propagation implemented.
- [x] Docker packaging implemented.
- [x] GitHub Actions CI implemented.
- [ ] Authentication and authorization implemented.
- [ ] Cloud deployment pipeline implemented.

## Documentation Controls

- [x] Project specification documented.
- [x] README documented.
- [x] Architecture notes documented.
- [x] Data contract documented.
- [x] Monitoring design documented.
- [x] Model card documented.
- [ ] Deployment guide documented.
- [ ] Dashboard screenshots included.
