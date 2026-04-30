from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from plugins.drug_catalog_tools.catalog import attach_catalog_scaffold, build_drug_template, load_json_records, save_json_records
from plugins.nhi_open_data_updater import NhiOpenDataUpdater
from plugins.ntuh_price_updater import NtuhPriceUpdater


def normalize_name(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def parse_input_list(path: Path) -> list[dict[str, str | None]]:
    if path.suffix.lower() == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        entries: list[dict[str, str | None]] = []
        for item in raw:
            if isinstance(item, str):
                entries.append({"generic_name": item.strip(), "trade_names": None})
            elif isinstance(item, dict):
                entries.append(
                    {
                        "generic_name": (item.get("generic_name") or "").strip(),
                        "trade_names": (item.get("trade_names") or "").strip() or None,
                    }
                )
        return [item for item in entries if item.get("generic_name")]

    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            rows = []
            for row in reader:
                rows.append(
                    {
                        "generic_name": (row.get("generic_name") or row.get("generic") or "").strip(),
                        "trade_names": (row.get("trade_names") or row.get("trade") or "").strip() or None,
                    }
                )
        return [item for item in rows if item.get("generic_name")]

    entries = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" in line:
            generic_name, trade_names = [part.strip() for part in line.split("|", 1)]
        else:
            generic_name, trade_names = line, None
        entries.append({"generic_name": generic_name, "trade_names": trade_names or None})
    return entries


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap a specialty catalog from a drug list.")
    parser.add_argument("--input", required=True, help="Input txt/csv/json drug list.")
    parser.add_argument("--output", required=True, help="Output catalog JSON path.")
    parser.add_argument("--specialty-id", required=True, help="Specialty id, e.g. oncology_lung.")
    parser.add_argument("--skip-ntuh", action="store_true", help="Skip NTUH self-pay update.")
    parser.add_argument("--skip-pdf", action="store_true", help="Skip NHI single-drug PDF download.")
    parser.add_argument("--pdf-cache-dir", help="Optional PDF cache dir for NHI rule PDFs.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    pdf_cache_dir = Path(args.pdf_cache_dir).resolve() if args.pdf_cache_dir else None

    requested = parse_input_list(input_path)
    existing = load_json_records(output_path) if output_path.exists() else []
    existing_by_name = {normalize_name(item.get("generic_name", "")): item for item in existing}
    selected_names: list[str] = []

    for item in requested:
        key = normalize_name(item["generic_name"] or "")
        if not key:
            continue
        selected_names.append(item["generic_name"] or "")
        if key in existing_by_name:
            record = existing_by_name[key]
            record["specialty_id"] = args.specialty_id
            if item.get("trade_names") and not record.get("trade_names"):
                record["trade_names"] = item["trade_names"]
            continue
        new_record = build_drug_template(
            item["generic_name"] or "",
            item.get("trade_names"),
            specialty_id=args.specialty_id,
        )
        existing.append(new_record)
        existing_by_name[key] = new_record

    nhi = NhiOpenDataUpdater()
    nhi_result = nhi.update_records(
        existing,
        selected_drugs=selected_names,
        skip_pdf=args.skip_pdf,
        pdf_cache_dir=pdf_cache_dir,
    )

    ntuh_result: dict[str, Any] | None = None
    if not args.skip_ntuh:
        ntuh = NtuhPriceUpdater()
        ntuh_result = ntuh.update_records(existing, selected_drugs=selected_names)

    for record in existing:
        if normalize_name(record.get("generic_name", "")) in {normalize_name(name) for name in selected_names}:
            attach_catalog_scaffold(record)

    save_json_records(output_path, existing)
    print(
        json.dumps(
            {
                "output": str(output_path),
                "specialty_id": args.specialty_id,
                "input_count": len(requested),
                "catalog_count": len(existing),
                "nhi": nhi_result,
                "ntuh": ntuh_result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
