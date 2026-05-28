from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.data_ingestion.loader import available_mappings, load_credit_dataset
from src.scoring.service import CreditRiskScoringService


def batch_score_file(
    input_path: str | Path,
    output_path: str | Path,
    mapping_name: str = "canonical",
    include_explanations: bool = True,
) -> pd.DataFrame:
    records = load_credit_dataset(input_path, mapping_name=mapping_name, require_target=False)
    service = CreditRiskScoringService()
    predictions = service.score_records(records, include_explanations=include_explanations)
    output = _build_output_frame(records, predictions)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(destination, index=False)
    return output


def _build_output_frame(records: pd.DataFrame, predictions: list[dict[str, object]]) -> pd.DataFrame:
    rows = []
    for row_index, prediction in enumerate(predictions):
        rows.append(
            {
                "record_id": row_index,
                "risk_probability": prediction["risk_probability"],
                "risk_tier": prediction["risk_tier"],
                "decision_threshold": prediction["decision_threshold"],
                "model_version": prediction["model_version"],
                "model_name": prediction["model_name"],
                "reason_codes": "|".join(prediction.get("reason_codes", [])),
                "scored_at": prediction["scored_at"],
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch score credit applicant records from a CSV file.")
    parser.add_argument("--input", required=True, help="Path to the source applicant CSV.")
    parser.add_argument("--output", required=True, help="Path to the output predictions CSV.")
    parser.add_argument("--mapping", default="canonical", choices=available_mappings(), help="Named dataset mapping.")
    parser.add_argument("--no-explanations", action="store_true", help="Disable reason-code generation for faster scoring.")
    args = parser.parse_args()

    output = batch_score_file(
        input_path=args.input,
        output_path=args.output,
        mapping_name=args.mapping,
        include_explanations=not args.no_explanations,
    )
    print(f"Scored {len(output)} records: {args.output}")


if __name__ == "__main__":
    main()
