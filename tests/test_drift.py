from src.monitoring.drift import drift_band, generate_drift_report, write_drift_report
from src.utils.sample_data import generate_credit_sample


def test_drift_band_thresholds() -> None:
    assert drift_band(0.05) == "stable"
    assert drift_band(0.12) == "moderate_drift"
    assert drift_band(0.30) == "significant_drift"


def test_drift_report_generates_feature_statuses(tmp_path) -> None:
    reference = generate_credit_sample(rows=100)
    current = reference.copy()
    current["debt_to_income"] = (current["debt_to_income"] + 0.25).clip(0, 1)

    report = write_drift_report(reference, current, output_path=tmp_path / "drift_report.json")

    assert report["reference_row_count"] == 100
    assert report["current_row_count"] == 100
    assert report["features"]
    assert (tmp_path / "drift_report.json").exists()


def test_drift_report_uses_numeric_columns_by_default() -> None:
    reference = generate_credit_sample(rows=80)
    current = generate_credit_sample(rows=80, random_state=99)

    report = generate_drift_report(reference, current)

    assert report["monitored_feature_count"] > 0
    assert all("psi" in feature for feature in report["features"])
