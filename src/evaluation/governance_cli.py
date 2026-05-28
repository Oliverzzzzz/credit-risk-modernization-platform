from __future__ import annotations

import argparse
from pathlib import Path

from src.evaluation.governance_report import write_governance_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a model governance report from training artifacts.")
    parser.add_argument("--output", default="artifacts/reports/model_governance_report.json", help="Output JSON report path.")
    args = parser.parse_args()

    report = write_governance_report(output_path=Path(args.output))
    print(f"Generated governance report for {report['model_name']}: {args.output}")


if __name__ == "__main__":
    main()
