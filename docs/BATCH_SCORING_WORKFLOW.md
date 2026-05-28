# Batch Scoring Workflow

Batch scoring simulates an enterprise portfolio review process where many applicant or loan records are scored together outside a real-time API call.

## Business Purpose

Financial institutions often need batch risk scoring for:

- daily or weekly portfolio reviews
- pre-screening applicant pools
- back-office underwriting queues
- monitoring risk tier distribution
- validating model behavior before deployment

## Workflow

1. A source CSV is mapped into the platform canonical schema.
2. The scoring service loads the trained model artifact and feature schema.
3. Applicant records are preprocessed and feature engineered.
4. The model generates default probabilities.
5. Each probability is mapped to a risk tier.
6. The batch output is written to CSV.
7. Each prediction is logged for auditability.

## Output Schema

Batch scoring output includes:

| Column | Description |
|---|---|
| `record_id` | Row-level identifier from the source file or generated row number. |
| `risk_probability` | Estimated probability of default. |
| `risk_tier` | Low, Medium, or High Risk. |
| `decision_threshold` | Active model decision threshold. |
| `model_version` | Model version used for scoring. |
| `model_name` | Selected model artifact name. |
| `reason_codes` | Pipe-delimited adverse risk drivers. |
| `scored_at` | Timestamp for the score. |

## Command

```bash
python -m src.scoring.batch_score \
  --input data/raw/applicants.csv \
  --output data/processed/batch_predictions.csv \
  --mapping canonical
```

Use `--mapping lending_club` or `--mapping give_me_some_credit` when scoring source-specific CSVs.

## Governance Notes

Batch scoring is not a replacement for human review or regulated credit decisioning. In this project, it demonstrates how an enterprise AI team can operationalize portfolio scoring while preserving traceability, model metadata, and reason codes.
