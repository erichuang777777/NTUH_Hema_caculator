from __future__ import annotations

import argparse
import json
from pathlib import Path

from .plugin import NtuhPriceUpdater


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update NTUH self-pay prices.")
    parser.add_argument("--data", required=True, help="Path to input JSON file.")
    parser.add_argument("--output", help="Optional output path. Defaults to overwriting --data.")
    parser.add_argument("--drug", action="append", default=[], help="Generic drug name to update. Can be repeated.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    updater = NtuhPriceUpdater()
    result = updater.update_file(
        data_path=Path(args.data).resolve(),
        output_path=Path(args.output).resolve() if args.output else None,
        selected_drugs=args.drug,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
