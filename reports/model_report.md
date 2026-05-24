# Model Report

This report is generated as a documentation placeholder for model governance review.

## Evaluation Focus

The platform evaluates models using ROC-AUC, precision, recall, F1, and confusion matrix. For credit risk workflows, recall is especially important when the business wants to identify likely defaults, while precision controls unnecessary manual reviews or rejected applicants.

## Business Tradeoff

False negatives may expose the institution to unexpected credit losses. False positives may reduce approval rates and create customer experience issues. Thresholds should therefore be selected with risk appetite, portfolio strategy, and fairness review in mind.

## Artifact Location

Train the model to generate detailed metrics in:

```text
artifacts/models/model_metrics.json
```

Global explainability outputs are written to:

```text
artifacts/models/global_explainability.json
```

The explainability artifact is intended for governance review and business interpretation. It should be reviewed together with model performance metrics, threshold policy, and portfolio risk appetite.
