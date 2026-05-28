from pathlib import Path


def test_dashboard_defines_expected_review_tabs() -> None:
    dashboard_source = Path("dashboard/streamlit_app.py").read_text(encoding="utf-8")

    assert "Portfolio" in dashboard_source
    assert "Model" in dashboard_source
    assert "Explainability" in dashboard_source
    assert "Monitoring" in dashboard_source
    assert "Governance" in dashboard_source
