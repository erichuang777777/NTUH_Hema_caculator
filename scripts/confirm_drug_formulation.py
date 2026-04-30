from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from plugins.drug_catalog_tools.catalog import confirm_primary_formulation, load_json_records, save_json_records

DATA_PATH = ROOT / "data" / "heme_drugs_clean.json"


def normalize_name(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Confirm and lock the primary formulation for a drug.")
    parser.add_argument("--drug", nargs="+", required=True, help="Generic drug name.")
    parser.add_argument("--drug-code", help="Confirmed NHI drug code.")
    parser.add_argument("--label", help="Confirmed formulation label.")
    parser.add_argument("--verified-by", help="Verifier name.")
    parser.add_argument("--note", help="Verification note.")
    parser.add_argument("--data", default=str(DATA_PATH), help="Path to the catalog JSON.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.drug_code and not args.label:
        raise SystemExit("Either --drug-code or --label is required.")

    data_path = Path(args.data).resolve()
    records = load_json_records(data_path)
    drug_name = " ".join(args.drug)
    drug = next((item for item in records if normalize_name(item.get("generic_name", "")) == normalize_name(drug_name)), None)
    if not drug:
        raise SystemExit(f"Drug not found: {drug_name}")

    candidates = drug.get("nhi_formulation_candidates") or []
    if candidates:
        matched = None
        for candidate in candidates:
            codes = [code for code in (candidate.get("drug_codes") or []) if code] or ([candidate.get("drug_code")] if candidate.get("drug_code") else [])
            if args.drug_code and args.drug_code in codes:
                matched = candidate
                break
            if args.label and candidate.get("label") == args.label:
                matched = candidate
                break
        if not matched:
            available = [
                {
                    "label": candidate.get("label"),
                    "drug_codes": [code for code in (candidate.get("drug_codes") or []) if code] or ([candidate.get("drug_code")] if candidate.get("drug_code") else []),
                }
                for candidate in candidates
            ]
            raise SystemExit("Confirmed formulation not found in candidates:\n" + json.dumps(available, ensure_ascii=False, indent=2))
        args.label = args.label or matched.get("label")
        if not args.drug_code:
            codes = [code for code in (matched.get("drug_codes") or []) if code] or ([matched.get("drug_code")] if matched.get("drug_code") else [])
            args.drug_code = codes[0] if codes else None

    confirm_primary_formulation(
        drug,
        confirmed_drug_code=args.drug_code,
        confirmed_formulation_label=args.label,
        verified_by=args.verified_by,
        note=args.note,
    )
    save_json_records(data_path, records)

    print(
        json.dumps(
            {
                "data_path": str(data_path),
                "drug": drug.get("generic_name"),
                "confirmed_drug_code": drug.get("manual_review", {}).get("confirmed_drug_code"),
                "confirmed_formulation_label": drug.get("manual_review", {}).get("confirmed_formulation_label"),
                "primary_formulation_confirmed": drug.get("manual_review", {}).get("primary_formulation_confirmed"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
