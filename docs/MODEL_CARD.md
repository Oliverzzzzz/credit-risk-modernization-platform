# Model Card: Credit Risk Modernization Platform

## Model Overview

This model card documents the current credit risk model used by the platform. The project simulates an enterprise financial services modernization workflow and should not be represented as a regulated production credit approval system.

## Intended Use

The model is intended to support:

- credit risk workflow modernization demonstrations
- borrower default risk scoring simulation
- explainable AI and model governance examples
- API-based decision support architecture
- portfolio review and batch scoring workflows

The model is not intended to make real credit approval, pricing, adverse action, or regulatory decisions.

## Model Inputs

The canonical schema includes borrower and loan attributes such as:

- annual income
- debt-to-income ratio
- loan amount
- interest rate
- employment length
- credit history length
- delinquency count
- revolving utilization
- open credit lines
- home ownership
- loan purpose

Feature engineering adds derived risk indicators such as loan-to-income, delinquency rate, utilization flags, and thin-file flags.

## Target

The target variable is:

```text
default_flag
```

It represents default or severe delinquency in the simulated training workflow.

## Model Candidates

The training pipeline compares:

- Logistic Regression
- Random Forest
- XGBoost

The selected model is determined by ROC-AUC on the holdout test set.

## Evaluation Metrics

The model is evaluated using:

- ROC-AUC
- precision
- recall
- F1 score
- confusion matrix

## Threshold Policy

The platform stores both the default classification threshold and an optimized threshold. The optimized threshold is selected by F1 score to balance precision and recall for review-oriented risk workflows.

Thresholds should be reviewed with business risk appetite before use in real decisioning.

## Explainability

The platform supports:

- local borrower-level reason codes
- global feature importance artifacts
- SHAP-based explanations when available
- model-native fallback explanations

Reason codes are intended to support interpretability and review, not automated regulatory adverse action notices.

## Monitoring Expectations

The platform includes lightweight monitoring for:

- prediction volume
- score distribution
- risk tier distribution
- prediction logs
- PSI-based drift reports
- data quality reports

Production systems would require delayed-label performance monitoring, fairness analysis, audit controls, and model retraining governance.

## Limitations

Current limitations:

- development fixture data is synthetic unless a public dataset is supplied
- no fairness or protected-class analysis has been implemented
- no model registry or approval workflow is included
- no delayed-label performance monitoring exists
- no production access controls are implemented
- no regulatory compliance claim is made

## Governance Position

This model card documents an enterprise-style AI engineering project. It is designed for portfolio and interview demonstration, showing awareness of model risk, explainability, monitoring, and deployment controls.
