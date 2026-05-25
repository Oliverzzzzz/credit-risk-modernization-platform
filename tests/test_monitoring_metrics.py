from src.monitoring.metrics import ApiMetrics


def test_api_metrics_tracks_score_distribution() -> None:
    metrics = ApiMetrics()

    metrics.record_prediction("Low Risk", 0.12)
    metrics.record_prediction("High Risk", 0.72)

    payload = metrics.as_dict()

    assert payload["prediction_count"] == 2
    assert payload["risk_tier_counts"]["Low Risk"] == 1
    assert payload["score_distribution"]["average"] == 0.42
    assert payload["score_distribution"]["min"] == 0.12
    assert payload["score_distribution"]["max"] == 0.72
