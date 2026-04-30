from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.site_builder import build_site
from core.specialty_loader import load_specialty_module


def build_specialty_site(
    *,
    specialty: str,
    source_data: str | Path | None = None,
    output_json: str | Path | None = None,
    output_html: str | Path | None = None,
) -> dict[str, Any]:
    module = load_specialty_module(specialty)
    site_config = dict(getattr(module, "SITE_CONFIG", {}) or {})

    source_path = Path(source_data or site_config.get("default_source_data") or "").resolve()
    output_json_path = Path(output_json or site_config.get("default_output_json") or "").resolve()
    output_html_path = Path(output_html or site_config.get("default_output_html") or "").resolve()

    if not source_path:
        raise ValueError("source_data is required")
    if not output_json_path or not output_html_path:
        raise ValueError("output_json and output_html are required")

    drugs = json.loads(source_path.read_text(encoding="utf-8"))
    drugs = module.apply_rules(drugs)
    html = build_site(
        drugs=drugs,
        site_config=site_config,
        output_html_path=output_html_path,
        output_json_path=output_json_path,
    )
    return {
        "specialty": specialty,
        "site_config": site_config,
        "source_path": source_path,
        "output_json_path": output_json_path,
        "output_html_path": output_html_path,
        "drugs": drugs,
        "html": html,
    }
