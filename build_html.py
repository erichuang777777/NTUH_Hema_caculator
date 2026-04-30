"""
Hematology site wrapper.

The generic HTML/CSS/JS site builder now lives in `core.site_builder`.
This file only loads the heme catalog, applies heme-specific rules, and
writes `data/heme_final.json` + `index.html`.
"""

from __future__ import annotations

from collections import Counter

from core.build_pipeline import build_specialty_site


def main() -> int:
    result = build_specialty_site(specialty="heme")
    drugs = result["drugs"]
    html = result["html"]

    print(f"Done: {len(html):,} chars, {len(html.splitlines())} lines")
    print("\n資料缺漏警告藥品：")
    for drug in drugs:
        if drug.get("data_note"):
            print(f"  {drug['generic_name']} ({drug['trade_names']}) - id={drug['id']}")

    print("\n治療線來源摘要：")
    src_count = Counter(drug.get("therapy_line_source", "?") for drug in drugs)
    for src, cnt in src_count.items():
        print(f"  {src}: {cnt} 種")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
