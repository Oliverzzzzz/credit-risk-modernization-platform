from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.utils.paths import MODEL_DIR, REPORT_ARTIFACT_DIR, ensure_project_directories


def build_governance_report(model_dir: Path = MODEL_DIR) -> dict[str, Any]:
    metadata = _read_json(model_dir / "model_metadata.json")
    metrics = _read_json(model_dir / "model_metrics.json")
    explainability = _read_json(model_dir / "global_explainability.json")

    selected_model = metadata["model_name"]
    selected_metrics = metrics[selected_model]
    return {
        "model_name": selected_model,
        "model_version": metadata["model_version"],
        "target_column": metadata["target_column"],
        "feature_count": metadata["feature_count"],
        "threshold_policy": metadata.get("threshold_policy", {}),
        "default_metrics": selected_metrics.get("default", {}),
        "optimized_metrics": selected_metrics.get("optimized", {}),
        "top_risk_drivers": explainability.get("top_features", [])[:10],
        "governance_summary": {
            "intended_use": "Portfolio demonstration and enterprise modernization simulation.",
            "not_for_use": "Real credit approval, pricing, adverse action, or regulatory decisioning.",
            "primary_risks": [
                "Synthetic or externally mapped data may not represent production borrower populations.",
                "Fairness analysis is not yet implemented.",
                "Delayed-label monitoring is not yet implemented.",
            ],
            "required_reviews_before_production": [
                "Data lineage review",
                "Fairness and bias assessment",
                "Model risk management approval",
                "Security and access control review",
                "Production monitoring and retraining plan",
            ],
        },
    }


def write_governance_report(output_path: Path | None = None, model_dir: Path = MODEL_DIR) -> dict[str, Any]:
    ensure_project_directories()
    report = build_governance_report(model_dir=model_dir)
    destination = output_path or REPORT_ARTIFACT_DIR / "model_governance_report.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required governance artifact is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
