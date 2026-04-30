from __future__ import annotations

import argparse
import json
from pathlib import Path

from .plugin import NhiOpenDataUpdater


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update drug metadata from NHI official open data.")
    parser.add_argument("--data", required=True, help="Path to input JSON file.")
    parser.add_argument("--output", help="Optional output path. Defaults to overwriting --data.")
    parser.add_argument("--drug", action="append", default=[], help="Generic drug name to update. Can be repeated.")
    parser.add_argument("--skip-pdf", action="store_true", help="Skip downloading individual reimbursement-rule PDFs.")
    parser.add_argument("--pdf-cache-dir", help="Directory used to cache downloaded reimbursement-rule PDFs.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    updater = NhiOpenDataUpdater()
    result = updater.update_file(
        data_path=Path(args.data).resolve(),
        output_path=Path(args.output).resolve() if args.output else None,
        selected_drugs=args.drug,
        skip_pdf=args.skip_pdf,
        pdf_cache_dir=Path(args.pdf_cache_dir).resolve() if args.pdf_cache_dir else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
