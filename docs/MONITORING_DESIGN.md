# Monitoring Design

This document defines the current monitoring scope for the credit risk modernization platform. The goal is to simulate enterprise monitoring patterns without overclaiming full production observability.

## Monitoring Objectives

The platform should help answer:

- Is the scoring API healthy?
- How many predictions have been served?
- What risk tiers are being assigned?
- Are prediction score distributions changing?
- Are input feature distributions drifting from training reference data?
- Are audit logs available for review?

## Current Monitoring Components

| Component | Purpose |
|---|---|
| API counters | Track health checks, prediction calls, and batch calls. |
| Prediction logs | Store structured JSONL records for audit review. |
| Drift utilities | Compare reference and current feature distributions using PSI. |
| Dashboard views | Surface prediction activity and model artifacts for review. |

## Drift Signal

The initial drift implementation uses Population Stability Index. PSI compares the distribution of a reference dataset against a current dataset. It is commonly used in risk analytics as a lightweight monitoring signal.

Interpretation bands:

| PSI Value | Interpretation |
|---:|---|
| `< 0.10` | Stable |
| `0.10 - 0.25` | Moderate drift |
| `> 0.25` | Significant drift |

## Report Output

Drift reports are stored as JSON artifacts:

```text
artifacts/reports/drift_report.json
```

## Enterprise Extension Points

Future monitoring improvements can include:

- Prometheus metrics
- Grafana dashboards
- Evidently reports
- model performance monitoring with delayed labels
- automated drift alerts
- centralized log aggregation
- model retraining triggers
