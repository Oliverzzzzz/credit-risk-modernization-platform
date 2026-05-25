from src.training.train_model import train_credit_risk_model
from src.utils.sample_data import generate_credit_sample


def test_training_pipeline_creates_metrics(tmp_path) -> None:
    data = generate_credit_sample(rows=160)
    result = train_credit_risk_model(data, tmp_path)

    assert "model_name" in result["metadata"]
    assert "threshold_policy" in result["metadata"]
    assert "logistic_regression" in result["metrics"]
    assert result["global_explainability"]["top_features"]
    assert result["data_quality"]["status"] == "pass"
    assert (tmp_path / "credit_risk_model.joblib").exists()
    assert (tmp_path / "model_metrics.json").exists()
    assert (tmp_path / "global_explainability.json").exists()
