from __future__ import annotations

import argparse

from src.data_ingestion.loader import available_mappings, load_credit_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Map a source credit CSV into the canonical platform schema.")
    parser.add_argument("--input", required=True, help="Path to the source CSV.")
    parser.add_argument("--output", required=True, help="Path for the canonical output CSV.")
    parser.add_argument("--mapping", default="canonical", choices=available_mappings(), help="Named dataset mapping.")
    parser.add_argument("--no-target", action="store_true", help="Use when mapping scoring data without default labels.")
    args = parser.parse_args()

    mapped = load_credit_dataset(args.input, mapping_name=args.mapping, require_target=not args.no_target)
    mapped.to_csv(args.output, index=False)
    print(f"Mapped {len(mapped)} rows using '{args.mapping}' mapping: {args.output}")


if __name__ == "__main__":
    main()
