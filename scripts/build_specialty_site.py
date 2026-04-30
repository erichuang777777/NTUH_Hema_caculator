from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.build_pipeline import build_specialty_site


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a specialty site using the generic site builder.")
    parser.add_argument("--specialty", required=True, help="Specialty module name, e.g. heme, lung, breast.")
    parser.add_argument("--data", help="Source catalog JSON path. Falls back to specialty config default.")
    parser.add_argument("--output-json", help="Output JSON path. Falls back to specialty config default.")
    parser.add_argument("--output-html", help="Output HTML path. Falls back to specialty config default.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = build_specialty_site(
        specialty=args.specialty,
        source_data=args.data,
        output_json=args.output_json,
        output_html=args.output_html,
    )

    drugs = result["drugs"]
    html = result["html"]
    print(
        json.dumps(
            {
                "specialty": result["specialty"],
                "source_path": str(result["source_path"]),
                "output_json_path": str(result["output_json_path"]),
                "output_html_path": str(result["output_html_path"]),
                "html_chars": len(html),
                "drug_count": len(drugs),
                "therapy_line_source_summary": Counter(drug.get("therapy_line_source", "?") for drug in drugs),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
