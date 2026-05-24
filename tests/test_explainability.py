from src.explainability.shap_explainer import CreditRiskExplainer
from src.feature_engineering.features import CreditFeatureEngineer, align_features
from src.preprocessing.pipeline import CreditDataPreprocessor
from src.training.train_model import train_credit_risk_model
from src.utils.sample_data import generate_credit_sample


def test_explainer_returns_reason_codes(tmp_path) -> None:
    data = generate_credit_sample(rows=180)
    result = train_credit_risk_model(data, tmp_path)
    clean = CreditDataPreprocessor(require_target=True).fit_transform(data.head(1))
    features = CreditFeatureEngineer().transform(clean).drop(columns=["default_flag"])
    features = align_features(features, result["metadata"]["feature_names"])

    explanation = CreditRiskExplainer().explain_instance(result["model"], features)

    assert explanation.reason_codes
    assert explanation.top_features
