from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_endpoint() -> None:
    payload = {
        "annual_income": 85000,
        "debt_to_income": 0.28,
        "loan_amount": 18000,
        "interest_rate": 0.11,
        "employment_length_years": 6,
        "credit_history_years": 9,
        "delinquency_count": 0,
        "revolving_utilization": 0.34,
        "open_credit_lines": 7,
        "home_ownership": "MORTGAGE",
        "loan_purpose": "debt_consolidation",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "risk_probability" in body
    assert body["risk_tier"] in {"Low Risk", "Medium Risk", "High Risk"}
