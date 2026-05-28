from src.scoring.batch_score import batch_score_file
from src.utils.sample_data import generate_credit_sample


def test_batch_score_file_writes_predictions(tmp_path) -> None:
    input_path = tmp_path / "applicants.csv"
    output_path = tmp_path / "predictions.csv"
    generate_credit_sample(rows=8).drop(columns=["default_flag"]).to_csv(input_path, index=False)

    predictions = batch_score_file(input_path, output_path, include_explanations=False)

    assert output_path.exists()
    assert len(predictions) == 8
    assert {"record_id", "risk_probability", "risk_tier", "model_version"}.issubset(predictions.columns)
    assert predictions["risk_tier"].isin(["Low Risk", "Medium Risk", "High Risk"]).all()
