from src.data_ingestion.quality import generate_data_quality_report, write_data_quality_report
from src.utils.sample_data import generate_credit_sample


def test_quality_report_passes_for_valid_sample(tmp_path) -> None:
    data = generate_credit_sample(rows=20)
    output_path = tmp_path / "data_quality_report.json"

    report = write_data_quality_report(data, output_path=output_path)

    assert report["status"] == "pass"
    assert report["row_count"] == 20
    assert output_path.exists()
    assert report["target_balance"]["positive_count"] >= 0


def test_quality_report_flags_missing_columns() -> None:
    data = generate_credit_sample(rows=10).drop(columns=["annual_income"])

    report = generate_data_quality_report(data)

    assert report["status"] == "fail"
    assert "annual_income" in report["missing_columns"]


def test_quality_report_flags_range_violations() -> None:
    data = generate_credit_sample(rows=10)
    data.loc[0, "interest_rate"] = 1.8

    report = generate_data_quality_report(data)

    assert report["status"] == "fail"
    assert report["numeric_ranges"]["interest_rate"]["above_max_count"] == 1
