from src.evaluation.governance_report import write_governance_report
from src.training.train_model import train_credit_risk_model
from src.utils.sample_data import generate_credit_sample


def test_governance_report_uses_model_artifacts(tmp_path) -> None:
    train_credit_risk_model(generate_credit_sample(rows=180), output_dir=tmp_path)

    report = write_governance_report(output_path=tmp_path / "governance.json", model_dir=tmp_path)

    assert report["model_name"]
    assert report["feature_count"] > 0
    assert report["optimized_metrics"]
    assert report["top_risk_drivers"]
    assert "not_for_use" in report["governance_summary"]
    assert (tmp_path / "governance.json").exists()
