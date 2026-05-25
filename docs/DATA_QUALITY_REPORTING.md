# Data Quality Reporting

Data quality checks are a required control in enterprise ML systems. Before a credit risk model is trained or a portfolio is scored, the platform should summarize whether the dataset is complete, valid, and consistent with the expected schema.

## Reporting Goals

The data quality report should help answer:

- Are all required columns present?
- Which columns contain missing values?
- Do numeric fields fall within expected business ranges?
- Are categorical values concentrated in unexpected buckets?
- Is the target variable balanced enough to support model training?
- How many rows are available after ingestion?

## Current Report Scope

The initial report includes:

- row count
- column count
- missing value summary
- numeric range validation
- categorical distribution summary
- target balance summary when `default_flag` is present

## Expected Output

Reports are persisted as JSON artifacts so they can be used by CI, dashboards, or future governance workflows.

Default location:

```text
artifacts/reports/data_quality_report.json
```

## Enterprise Extension Points

Future versions can add:

- Great Expectations checks
- schema versioning
- alert thresholds
- rejected row quarantine
- data owner sign-off
- trend analysis across reporting dates
- integration with model retraining gates
