from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils.paths import LOG_DIR, MODEL_DIR, REPORT_ARTIFACT_DIR


st.set_page_config(page_title="Credit Risk Modernization Dashboard", layout="wide")

MODEL_METRICS_PATH = MODEL_DIR / "model_metrics.json"
MODEL_METADATA_PATH = MODEL_DIR / "model_metadata.json"
EXPLAINABILITY_PATH = MODEL_DIR / "global_explainability.json"
PREDICTION_LOG_PATH = LOG_DIR / "predictions.jsonl"
DATA_QUALITY_PATH = REPORT_ARTIFACT_DIR / "data_quality_report.json"
GOVERNANCE_PATH = REPORT_ARTIFACT_DIR / "model_governance_report.json"
DRIFT_PATH = REPORT_ARTIFACT_DIR / "drift_report.json"


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_prediction_logs(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return pd.DataFrame(records)


def metric_value(value: Any, digits: int = 3) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


metadata = read_json(MODEL_METADATA_PATH)
metrics = read_json(MODEL_METRICS_PATH)
explainability = read_json(EXPLAINABILITY_PATH)
data_quality = read_json(DATA_QUALITY_PATH)
governance = read_json(GOVERNANCE_PATH)
drift = read_json(DRIFT_PATH)
logs = read_prediction_logs(PREDICTION_LOG_PATH)

st.title("Credit Risk Modernization Dashboard")
st.caption("Internal portfolio risk, model governance, and monitoring review surface.")

overview_tab, model_tab, explainability_tab, monitoring_tab, governance_tab = st.tabs(
    ["Portfolio", "Model", "Explainability", "Monitoring", "Governance"]
)

with overview_tab:
    st.subheader("Portfolio Overview")
    total_predictions = len(logs)
    high_risk_count = int((logs["risk_tier"] == "High Risk").sum()) if "risk_tier" in logs else 0
    avg_score = float(logs["risk_probability"].mean()) if "risk_probability" in logs and not logs.empty else None
    model_name = metadata.get("model_name") if metadata else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Predictions Logged", total_predictions)
    c2.metric("High Risk Count", high_risk_count)
    c3.metric("Average Risk Score", metric_value(avg_score))
    c4.metric("Active Model", model_name or "N/A")

    if not logs.empty and "risk_tier" in logs:
        left, right = st.columns(2)
        with left:
            tier_counts = logs["risk_tier"].value_counts().reset_index()
            tier_counts.columns = ["risk_tier", "count"]
            st.plotly_chart(px.bar(tier_counts, x="risk_tier", y="count", title="Risk Tier Distribution"), use_container_width=True)
        with right:
            st.plotly_chart(px.histogram(logs, x="risk_probability", nbins=20, title="Risk Score Distribution"), use_container_width=True)

        st.subheader("Recent Predictions")
        display_columns = [column for column in ["logged_at", "risk_probability", "risk_tier", "model_version"] if column in logs.columns]
        st.dataframe(logs[display_columns].tail(25), use_container_width=True)
    else:
        st.info("No prediction logs are available. Run API scoring or batch scoring to populate this view.")

with model_tab:
    st.subheader("Model Performance")
    if metadata:
        c1, c2, c3 = st.columns(3)
        c1.metric("Model Version", metadata.get("model_version", "N/A"))
        c2.metric("Feature Count", metadata.get("feature_count", "N/A"))
        c3.metric("Decision Threshold", metric_value(metadata.get("threshold_policy", {}).get("optimized_threshold")))

    if metrics and metadata:
        selected_model = metadata["model_name"]
        selected_metrics = metrics[selected_model]
        default_metrics = selected_metrics.get("default", {})
        optimized_metrics = selected_metrics.get("optimized", {})
        comparison = pd.DataFrame(
            [
                {"metric": "ROC-AUC", "default": default_metrics.get("roc_auc"), "optimized": optimized_metrics.get("roc_auc")},
                {"metric": "Precision", "default": default_metrics.get("precision"), "optimized": optimized_metrics.get("precision")},
                {"metric": "Recall", "default": default_metrics.get("recall"), "optimized": optimized_metrics.get("recall")},
                {"metric": "F1", "default": default_metrics.get("f1"), "optimized": optimized_metrics.get("f1")},
            ]
        )
        st.dataframe(comparison, use_container_width=True)
        st.plotly_chart(px.bar(comparison, x="metric", y=["default", "optimized"], barmode="group", title="Default vs Optimized Threshold Metrics"), use_container_width=True)
    else:
        st.info("Train the model to generate model metrics.")

with explainability_tab:
    st.subheader("Global Explainability")
    if explainability:
        importance = pd.DataFrame(explainability["top_features"])
        st.plotly_chart(px.bar(importance, x="importance", y="feature", orientation="h", title="Top Model Risk Drivers"), use_container_width=True)
        st.caption(explainability["governance_note"])
        st.dataframe(importance[["feature", "importance", "business_reason"]], use_container_width=True)
    else:
        st.info("Train the model to generate global explainability artifacts.")

with monitoring_tab:
    st.subheader("Monitoring And Data Quality")
    left, right = st.columns(2)
    with left:
        st.markdown("**Data Quality**")
        if data_quality:
            st.metric("Status", data_quality["status"].upper())
            st.metric("Rows", data_quality["row_count"])
            st.metric("Target Positive Rate", metric_value(data_quality.get("target_balance", {}).get("positive_rate")))
            missing_summary = pd.DataFrame(data_quality["missing_values"]).T.reset_index().rename(columns={"index": "column"})
            st.dataframe(missing_summary, use_container_width=True)
        else:
            st.info("No data quality report is available.")
    with right:
        st.markdown("**Drift**")
        if drift:
            st.metric("Overall Drift Status", drift["overall_status"])
            st.metric("Monitored Features", drift["monitored_feature_count"])
            st.dataframe(pd.DataFrame(drift["features"]), use_container_width=True)
        else:
            st.info("No drift report is available.")

with governance_tab:
    st.subheader("Governance Summary")
    if governance:
        c1, c2, c3 = st.columns(3)
        c1.metric("Governed Model", governance["model_name"])
        c2.metric("Model Version", governance["model_version"])
        c3.metric("Feature Count", governance["feature_count"])
        st.markdown("**Primary Risks**")
        for risk in governance["governance_summary"]["primary_risks"]:
            st.write(f"- {risk}")
        st.markdown("**Required Reviews Before Production**")
        for review in governance["governance_summary"]["required_reviews_before_production"]:
            st.write(f"- {review}")
    else:
        st.info("No model governance report is available.")
