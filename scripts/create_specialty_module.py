from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIALTIES_DIR = ROOT / "specialties"


def slugify(value: str) -> str:
    return "_".join(part for part in value.strip().lower().replace("-", "_").split() if part)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a new specialty module scaffold.")
    parser.add_argument("--name", required=True, help="Specialty folder name, e.g. lung or breast.")
    parser.add_argument("--title", required=True, help="Display title.")
    parser.add_argument("--subtitle", required=True, help="Header subtitle.")
    parser.add_argument("--specialty-id", required=True, help="Specialty id, e.g. oncology_lung.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    name = slugify(args.name)
    target = SPECIALTIES_DIR / name
    target.mkdir(parents=True, exist_ok=True)

    files = {
        "__init__.py": f'"""Specialty module: {name}."""\n',
        "config.py": (
            "SITE_CONFIG = {\n"
            f'    "specialty_id": "{args.specialty_id}",\n'
            f'    "html_title": "{args.title}",\n'
            f'    "header_title": "{args.title}",\n'
            f'    "header_subtitle": "{args.subtitle}",\n'
            '    "version_label": "v0.1",\n'
            '    "price_basis_label": "藥價基準待確認",\n'
            "}\n"
        ),
        "review_support.py": (
            "from __future__ import annotations\n\n\n"
            "def apply_review_support(drug: dict) -> None:\n"
            '    """Attach specialty-specific review schemas here."""\n'
            "    return None\n"
        ),
        "postprocess.py": (
            "from __future__ import annotations\n\n"
            f"from specialties.{name}.review_support import apply_review_support\n\n\n"
            "def apply_rules(drugs: list[dict]) -> list[dict]:\n"
            "    for drug in drugs:\n"
            "        drug.pop('review_support', None)\n"
            "        apply_review_support(drug)\n"
            "    return drugs\n"
        ),
        "README.md": (
            f"# {args.title}\n\n"
            "- 在 `postprocess.py` 放疾病標籤、治療線與資料校正規則\n"
            "- 在 `review_support.py` 放專科送審欄位 schema\n"
            "- 在 `config.py` 放站點標題與版本資訊\n"
        ),
    }

    for filename, content in files.items():
        path = target / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")

    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
