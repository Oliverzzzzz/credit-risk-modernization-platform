from __future__ import annotations

import argparse
from pathlib import Path

from src.data_ingestion.loader import available_mappings, load_credit_dataset
from src.data_ingestion.quality import write_data_quality_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a data quality report for credit risk datasets.")
    parser.add_argument("--input", required=True, help="Path to the source CSV.")
    parser.add_argument("--mapping", default="canonical", choices=available_mappings(), help="Named dataset mapping.")
    parser.add_argument("--output", default="artifacts/reports/data_quality_report.json", help="Output JSON report path.")
    parser.add_argument("--no-target", action="store_true", help="Use for scoring datasets without target labels.")
    args = parser.parse_args()

    data = load_credit_dataset(args.input, mapping_name=args.mapping, require_target=not args.no_target)
    report = write_data_quality_report(data, output_path=Path(args.output), require_target=not args.no_target)
    print(f"Data quality status: {report['status']} ({args.output})")


if __name__ == "__main__":
    main()
