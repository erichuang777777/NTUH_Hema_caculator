from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from plugins.drug_catalog_tools.catalog import build_drug_template


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a new scaffolded drug entry.")
    parser.add_argument("--generic-name", nargs="+", required=True, help="Generic drug name.")
    parser.add_argument("--trade-names", nargs="*", help="Trade name(s).")
    parser.add_argument("--specialty-id", default="oncology_heme", help="Specialty id, e.g. oncology_lung.")
    parser.add_argument("--output", required=True, help="Output JSON path.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    generic_name = " ".join(args.generic_name)
    trade_names = " ".join(args.trade_names) if args.trade_names else None
    entry = build_drug_template(generic_name, trade_names, specialty_id=args.specialty_id)
    output = Path(args.output).resolve()
    output.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "generic_name": generic_name, "specialty_id": args.specialty_id}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
