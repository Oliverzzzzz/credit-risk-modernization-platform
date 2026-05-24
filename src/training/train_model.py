from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.evaluation.metrics import evaluate_binary_classifier, optimize_threshold
from src.feature_engineering.features import CreditFeatureEngineer
from src.preprocessing.pipeline import CreditDataPreprocessor
from src.preprocessing.schema import TARGET_COLUMN
from src.utils.config import DEFAULT_MODEL_CONFIG
from src.utils.paths import MODEL_DIR, RAW_DATA_DIR, ensure_project_directories
from src.utils.sample_data import generate_credit_sample


def build_training_matrix(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    preprocessed = CreditDataPreprocessor(require_target=True).fit_transform(data)
    engineered = CreditFeatureEngineer().fit_transform(preprocessed)
    y = engineered[TARGET_COLUMN].astype(int)
    x = engineered.drop(columns=[TARGET_COLUMN])
    return x, y


def train_models(x_train: pd.DataFrame, y_train: pd.Series) -> dict[str, object]:
    class_weight = "balanced"
    models: dict[str, object] = {
        "logistic_regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(max_iter=1000, class_weight=class_weight, random_state=DEFAULT_MODEL_CONFIG.random_state),
                ),
            ]
        ).fit(x_train, y_train),
        "random_forest": RandomForestClassifier(
            n_estimators=250,
            max_depth=8,
            min_samples_leaf=8,
            class_weight=class_weight,
            random_state=DEFAULT_MODEL_CONFIG.random_state,
            n_jobs=-1,
        ).fit(x_train, y_train),
    }
    try:
        from xgboost import XGBClassifier

        positive_rate = y_train.mean()
        scale_pos_weight = (1 - positive_rate) / positive_rate if positive_rate > 0 else 1
        models["xgboost"] = XGBClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            scale_pos_weight=scale_pos_weight,
            random_state=DEFAULT_MODEL_CONFIG.random_state,
        ).fit(x_train, y_train)
    except ImportError:
        pass
    return models


def select_best_model(models: dict[str, object], x_test: pd.DataFrame, y_test: pd.Series) -> tuple[str, object, dict[str, object]]:
    results: dict[str, dict[str, float]] = {}
    for name, model in models.items():
        probabilities = model.predict_proba(x_test)[:, 1]
        threshold_policy = optimize_threshold(y_test.to_numpy(), probabilities)
        results[name] = {
            "default": evaluate_binary_classifier(y_test.to_numpy(), probabilities),
            "optimized": evaluate_binary_classifier(
                y_test.to_numpy(),
                probabilities,
                threshold=threshold_policy["optimized_threshold"],
            ),
            "threshold_policy": threshold_policy,
        }
    best_name = max(results, key=lambda model_name: results[model_name]["default"]["roc_auc"])
    return best_name, models[best_name], results


def train_credit_risk_model(data: pd.DataFrame, output_dir: Path = MODEL_DIR) -> dict[str, object]:
    ensure_project_directories()
    x, y = build_training_matrix(data)
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=DEFAULT_MODEL_CONFIG.test_size,
        random_state=DEFAULT_MODEL_CONFIG.random_state,
        stratify=y,
    )

    models = train_models(x_train, y_train)
    best_name, best_model, results = select_best_model(models, x_test, y_test)

    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, output_dir / "credit_risk_model.joblib")

    metadata = {
        "model_name": best_name,
        "model_version": DEFAULT_MODEL_CONFIG.model_version,
        "target_column": TARGET_COLUMN,
        "feature_count": len(x.columns),
        "feature_names": list(x.columns),
        "threshold_policy": results[best_name]["threshold_policy"],
    }
    (output_dir / "model_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (output_dir / "model_metrics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    (output_dir / "feature_schema.json").write_text(json.dumps({"features": list(x.columns)}, indent=2), encoding="utf-8")

    return {"model": best_model, "metadata": metadata, "metrics": results}


def load_training_data(input_path: str | None, generate_sample: bool) -> pd.DataFrame:
    if generate_sample or input_path is None:
        sample = generate_credit_sample()
        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        sample.to_csv(RAW_DATA_DIR / "sample_credit_applications.csv", index=False)
        return sample
    return pd.read_csv(input_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train credit risk models.")
    parser.add_argument("--input", help="Path to a training CSV.", default=None)
    parser.add_argument("--generate-sample", action="store_true", help="Generate development fixture data before training.")
    args = parser.parse_args()

    data = load_training_data(args.input, args.generate_sample)
    result = train_credit_risk_model(data)
    print(json.dumps({"selected_model": result["metadata"]["model_name"], "metrics": result["metrics"]}, indent=2))


if __name__ == "__main__":
    main()
