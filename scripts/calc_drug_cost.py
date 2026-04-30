from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from plugins.drug_catalog_tools.catalog import load_json_records
from plugins.drug_catalog_tools.dose_engine import calculate_course_cost

DEFAULT_DATA = ROOT / "data" / "heme_drugs_clean.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calculate drug cycle / course cost.")
    parser.add_argument("--data", default=str(DEFAULT_DATA), help="Drug catalog JSON path.")
    parser.add_argument("--drug", required=True, help="Generic drug name.")
    parser.add_argument("--profile-id", default="default", help="Dosing profile id.")
    parser.add_argument("--weight-kg", type=float, help="Weight in kg.")
    parser.add_argument("--height-cm", type=float, help="Height in cm.")
    parser.add_argument("--bsa", type=float, help="Body surface area.")
    parser.add_argument("--gfr", type=float, help="GFR for AUC dosing.")
    parser.add_argument("--target-auc", type=float, help="Target AUC for AUC dosing.")
    parser.add_argument("--cycles", type=int, default=1, help="Number of cycles.")
    parser.add_argument("--pricing", choices=["nhi_price", "ntuh_self_pay_price"], default="nhi_price")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    records = load_json_records(args.data)
    drug = next((d for d in records if d["generic_name"].lower() == args.drug.lower()), None)
    if drug is None:
        raise SystemExit(f"Drug not found: {args.drug}")
    profile = next((p for p in drug.get("dosing_profiles", []) if p.get("profile_id") == args.profile_id), None)
    if profile is None:
        raise SystemExit(f"Dosing profile not found: {args.profile_id}")

    result = calculate_course_cost(
        drug,
        profile,
        weight_kg=args.weight_kg,
        height_cm=args.height_cm,
        bsa=args.bsa,
        gfr=args.gfr,
        target_auc=args.target_auc,
        cycles=args.cycles,
        pricing=args.pricing,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
