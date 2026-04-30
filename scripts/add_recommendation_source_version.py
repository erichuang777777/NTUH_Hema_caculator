from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from plugins.drug_catalog_tools.catalog import add_recommendation_source_version, load_json_records, save_json_records

DATA_PATH = ROOT / "data" / "heme_drugs_clean.json"


def normalize_name(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Append a versioned recommendation/guideline source to a drug.")
    parser.add_argument("--drug", nargs="+", required=True, help="Generic drug name.")
    parser.add_argument("--source-type", required=True, help="Source type, e.g. NCCN, Guideline, NHI, NTUH, Local.")
    parser.add_argument("--source-name", required=True, help="Display source name.")
    parser.add_argument("--category", default="general", help="Category, e.g. coverage_line, recommendation, self_pay_pricing.")
    parser.add_argument("--date", help="Effective date / query date, e.g. 2026-04-30 or 1150401.")
    parser.add_argument("--recommendation", required=True, help="Recommendation or conclusion for this version.")
    parser.add_argument("--evidence-note", default="", help="Evidence note / interpretation note.")
    parser.add_argument("--reference-code", action="append", default=[], help="Repeatable reference code, e.g. 9.71.")
    parser.add_argument("--source-url", help="Reference URL.")
    parser.add_argument("--verified-by", help="Operator name.")
    parser.add_argument("--data", default=str(DATA_PATH), help="Path to the catalog JSON.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    data_path = Path(args.data).resolve()
    records = load_json_records(data_path)
    drug_name = " ".join(args.drug)
    drug = next((item for item in records if normalize_name(item.get("generic_name", "")) == normalize_name(drug_name)), None)
    if not drug:
        raise SystemExit(f"Drug not found: {drug_name}")

    add_recommendation_source_version(
        drug,
        source_type=args.source_type,
        source_name=args.source_name,
        category=args.category,
        recommendation=args.recommendation,
        effective_or_query_date=args.date,
        evidence_note=args.evidence_note,
        reference_codes=args.reference_code,
        source_url=args.source_url,
        verified_by=args.verified_by,
    )
    save_json_records(data_path, records)
    print(
        json.dumps(
            {
                "data_path": str(data_path),
                "drug": drug.get("generic_name"),
                "source_type": args.source_type,
                "source_name": args.source_name,
                "category": args.category,
                "date": args.date,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
