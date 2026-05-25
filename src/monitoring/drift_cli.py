from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.monitoring.drift import write_drift_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a PSI drift report from reference and current datasets.")
    parser.add_argument("--reference", required=True, help="Path to the reference CSV.")
    parser.add_argument("--current", required=True, help="Path to the current CSV.")
    parser.add_argument("--output", default="artifacts/reports/drift_report.json", help="Output JSON report path.")
    args = parser.parse_args()

    reference = pd.read_csv(args.reference)
    current = pd.read_csv(args.current)
    report = write_drift_report(reference, current, output_path=Path(args.output))
    print(f"Drift status: {report['overall_status']} ({args.output})")


if __name__ == "__main__":
    main()
