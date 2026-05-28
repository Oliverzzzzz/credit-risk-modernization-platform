from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _valid_payload() -> dict[str, object]:
    return {
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


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["artifacts"]["model"] is True


def test_predict_endpoint() -> None:
    response = client.post("/predict", json=_valid_payload(), headers={"X-Request-ID": "test-request-1"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-1"
    body = response.json()
    assert "risk_probability" in body
    assert body["risk_tier"] in {"Low Risk", "Medium Risk", "High Risk"}


def test_predict_rejects_invalid_category() -> None:
    payload = _valid_payload()
    payload["home_ownership"] = "VACATION_HOME"

    response = client.post("/predict", json=payload, headers={"X-Request-ID": "bad-category"})

    assert response.status_code == 422
    assert response.headers["X-Request-ID"] == "bad-category"
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_batch_predict_enforces_size_limit() -> None:
    payload = {"applicants": [_valid_payload() for _ in range(101)]}

    response = client.post("/batch_predict", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_batch_predict_accepts_valid_batch() -> None:
    payload = {"applicants": [_valid_payload(), _valid_payload()]}

    response = client.post("/batch_predict", json=payload)

    assert response.status_code == 200
    assert response.json()["count"] == 2
