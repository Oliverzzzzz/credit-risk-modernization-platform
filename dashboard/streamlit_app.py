from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils.paths import LOG_DIR, MODEL_DIR


st.set_page_config(page_title="Credit Risk Modernization Dashboard", layout="wide")
st.title("Credit Risk Modernization Dashboard")

metrics_path = MODEL_DIR / "model_metrics.json"
log_path = LOG_DIR / "predictions.jsonl"

left, right = st.columns(2)

with left:
    st.subheader("Model Evaluation")
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        st.json(metrics)
    else:
        st.info("Train the model to generate evaluation artifacts.")

with right:
    st.subheader("Prediction Activity")
    if log_path.exists():
        records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        logs = pd.DataFrame(records)
        st.metric("Predictions Logged", len(logs))
        if "risk_tier" in logs:
            fig = px.histogram(logs, x="risk_tier", title="Risk Tier Distribution")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No prediction logs are available yet.")

st.subheader("Portfolio Monitoring Notes")
st.write(
    "This dashboard summarizes model artifacts and scoring logs. In an enterprise deployment, "
    "this view would connect to governed data stores, model registry metadata, and observability systems."
)
