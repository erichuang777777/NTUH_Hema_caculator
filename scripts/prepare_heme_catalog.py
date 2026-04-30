from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from plugins.drug_catalog_tools.catalog import COMMON_REGIMENS, attach_catalog_scaffold, load_json_records, save_json_records

DATA_PATH = ROOT / "data" / "heme_drugs_clean.json"
REGIMEN_PATH = ROOT / "data" / "common_regimens.json"


def main() -> int:
    records = load_json_records(DATA_PATH)
    for drug in records:
        attach_catalog_scaffold(drug)
    save_json_records(DATA_PATH, records)
    REGIMEN_PATH.write_text(json.dumps(COMMON_REGIMENS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updated_drugs": len(records), "data_path": str(DATA_PATH), "regimen_path": str(REGIMEN_PATH)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
