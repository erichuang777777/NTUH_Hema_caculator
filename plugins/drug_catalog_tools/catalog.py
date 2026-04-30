from __future__ import annotations

import json
import math
import re
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any


COMMON_REGIMENS: list[dict[str, Any]] = [
    {
        "regimen_id": "r-chop",
        "display_name": "R-CHOP",
        "cycle_days": 21,
        "diseases": ["DLBCL", "NHL", "CLL/lymphoma overlap"],
        "components": [
            {"generic_name": "Rituximab", "dose_mode": "bsa", "dose_value": 375, "dose_unit": "mg/m2", "days": [1]},
            {"generic_name": "Cyclophosphamide", "dose_mode": "bsa", "dose_value": 750, "dose_unit": "mg/m2", "days": [1]},
            {"generic_name": "Doxorubicin", "dose_mode": "bsa", "dose_value": 50, "dose_unit": "mg/m2", "days": [1]},
            {"generic_name": "Vincristine", "dose_mode": "bsa", "dose_value": 1.4, "dose_unit": "mg/m2", "days": [1], "max_dose_mg": 2},
            {"generic_name": "Prednisone", "dose_mode": "fixed_daily", "dose_value": 100, "dose_unit": "mg", "days": [1, 2, 3, 4, 5]},
        ],
        "note": "標準 21 天週期，實際處方仍以主治醫師與病人體況調整。",
    },
    {
        "regimen_id": "br",
        "display_name": "Bendamustine + Rituximab",
        "cycle_days": 28,
        "diseases": ["CLL", "indolent lymphoma", "MCL"],
        "components": [
            {"generic_name": "Bendamustine", "dose_mode": "bsa", "dose_value": 90, "dose_unit": "mg/m2", "days": [1, 2]},
            {"generic_name": "Rituximab", "dose_mode": "bsa", "dose_value": 375, "dose_unit": "mg/m2", "days": [1]},
        ],
        "note": "常見於 CLL 或惰性淋巴瘤。",
    },
    {
        "regimen_id": "aza-ven",
        "display_name": "Azacitidine + Venetoclax",
        "cycle_days": 28,
        "diseases": ["AML"],
        "components": [
            {"generic_name": "Azacitidine", "dose_mode": "bsa", "dose_value": 75, "dose_unit": "mg/m2", "days": [1, 2, 3, 4, 5, 6, 7]},
            {"generic_name": "Venetoclax", "dose_mode": "fixed_daily", "dose_value": 400, "dose_unit": "mg", "days": list(range(1, 29))},
        ],
        "note": "實際 venetoclax 天數常依血球恢復與感染風險調整。",
    },
    {
        "regimen_id": "vrd",
        "display_name": "VRd",
        "cycle_days": 21,
        "diseases": ["myeloma"],
        "components": [
            {"generic_name": "Bortezomib", "dose_mode": "bsa", "dose_value": 1.3, "dose_unit": "mg/m2", "days": [1, 4, 8, 11]},
            {"generic_name": "Lenalidomide", "dose_mode": "fixed_daily", "dose_value": 25, "dose_unit": "mg", "days": list(range(1, 15))},
            {"generic_name": "Dexamethasone", "dose_mode": "fixed_daily", "dose_value": 40, "dose_unit": "mg", "days": [1, 8, 15]},
        ],
        "note": "多發性骨髓瘤常見誘導方案之一。",
    },
]


REGIMEN_GENERIC_MAP: dict[str, list[str]] = {
    "Rituximab": ["r-chop", "br"],
    "Cyclophosphamide": ["r-chop"],
    "Doxorubicin": ["r-chop"],
    "Bendamustine": ["br"],
    "Azacitidine": ["aza-ven"],
    "Venetoclax": ["aza-ven"],
    "Bortezomib": ["vrd"],
    "Lenalidomide": ["vrd"],
    "Dexamethasone": ["vrd"],
}

DISEASE_KEYWORDS: list[tuple[str, list[str]]] = [
    ("AML", ["急性骨髓性白血病", "acute myeloid leukemia", "aml"]),
    ("ALL", ["急性淋巴性白血病", "acute lymphoblastic leukemia", "all"]),
    ("CLL", ["慢性淋巴球性白血病", "chronic lymphocytic leukemia", "cll"]),
    ("CML", ["慢性骨髓性白血病", "chronic myeloid leukemia", "cml"]),
    ("MDS", ["骨髓增生不良症候群", "myelodysplastic syndrome", "mds"]),
    ("MPN", ["骨髓增生性腫瘤", "myeloproliferative", "mpn"]),
    ("lymphoma", ["淋巴瘤", "lymphoma"]),
    ("DLBCL", ["瀰漫性大b細胞淋巴瘤", "diffuse large b-cell lymphoma", "dlbcl"]),
    ("FL", ["濾泡性淋巴瘤", "follicular lymphoma"]),
    ("MCL", ["被套細胞淋巴瘤", "mantle cell lymphoma"]),
    ("WM", ["華氏巨球蛋白血症", "waldenstrom", "waldenström"]),
    ("myeloma", ["多發性骨髓瘤", "multiple myeloma", "myeloma"]),
    ("aplastic_anemia", ["再生不良性貧血", "aplastic anemia"]),
    ("itp", ["免疫性血小板減少症", "immune thrombocytopenia", "itp"]),
]


def load_json_records(path: str | Path) -> list[dict[str, Any]]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json_records(path: str | Path, data: list[dict[str, Any]]) -> None:
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def parse_strength_mg(value: str | None) -> float | None:
    if not value:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*mg", value, flags=re.I)
    return float(match.group(1)) if match else None


def infer_formulation_unit(value: str | None) -> str:
    if not value:
        return "unit"
    lowered = value.lower()
    if "cap" in lowered:
        return "cap"
    if "tab" in lowered:
        return "tab"
    if "vial" in lowered:
        return "vial"
    if "syringe" in lowered:
        return "syringe"
    return "unit"


def normalize_schedule(schedule: str | None) -> dict[str, int] | None:
    if not schedule:
        return None
    match = re.fullmatch(r"(\d+)\s*/\s*(\d+)", schedule.strip())
    if not match:
        return None
    return {"days_on": int(match.group(1)), "cycle_days": int(match.group(2))}


def candidate_codes(candidate: dict[str, Any]) -> list[str]:
    codes = [code for code in (candidate.get("drug_codes") or []) if code]
    if codes:
        return codes
    code = candidate.get("drug_code")
    return [code] if code else []


def matches_manual_confirmation(candidate: dict[str, Any], manual_review: dict[str, Any]) -> bool:
    confirmed_drug_code = manual_review.get("confirmed_drug_code")
    confirmed_label = manual_review.get("confirmed_formulation_label")
    if confirmed_drug_code and confirmed_drug_code in candidate_codes(candidate):
        return True
    if confirmed_label and candidate.get("label") == confirmed_label:
        return True
    return False


def find_confirmed_candidate(drug: dict[str, Any]) -> dict[str, Any] | None:
    manual_review = drug.get("manual_review") or {}
    candidates = drug.get("nhi_formulation_candidates") or []
    for candidate in candidates:
        if matches_manual_confirmation(candidate, manual_review):
            return candidate
    return None


def seed_manual_review(drug: dict[str, Any]) -> dict[str, Any]:
    current = deepcopy(drug.get("manual_review") or {})
    candidates = drug.get("nhi_formulation_candidates") or []
    distinct_labels = sorted({candidate.get("label") for candidate in candidates if candidate.get("label")})
    primary_formulation_confirmed = current.get("primary_formulation_confirmed", False)
    multi_formulation_pending = len(distinct_labels) > 1 and not primary_formulation_confirmed
    selected_zero_price = any(
        candidate.get("selected") and candidate.get("nhi_price") == 0 for candidate in candidates
    ) or drug.get("nhi_price") == 0
    default_priority = "high" if selected_zero_price else current.get("verification_priority", "routine")
    return {
        "is_verified": current.get("is_verified", False),
        "verification_priority": default_priority,
        "canonical_decision": current.get("canonical_decision", "pending"),
        "checked_fields": current.get("checked_fields", []),
        "primary_formulation_confirmed": primary_formulation_confirmed,
        "multi_formulation_pending": multi_formulation_pending,
        "candidate_formulation_count": len(distinct_labels),
        "confirmed_drug_code": current.get("confirmed_drug_code"),
        "confirmed_formulation_label": current.get("confirmed_formulation_label"),
        "regimen_mapping_confirmed": current.get("regimen_mapping_confirmed", False),
        "last_verified_at": current.get("last_verified_at"),
        "verified_by": current.get("verified_by"),
        "notes": current.get("notes", ""),
    }


def seed_record_versions(drug: dict[str, Any]) -> list[dict[str, Any]]:
    current = deepcopy(drug.get("record_versions") or [])
    if current:
        return current
    return [
        {
            "version": "catalog-v1",
            "event_type": "catalog_scaffold",
            "event_at": datetime.now().isoformat(timespec="seconds"),
            "summary": "初始化人工確認、多劑型與劑量計算欄位",
            "source": "local",
        }
    ]


def seed_formulations(drug: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = drug.get("nhi_formulation_candidates") or []
    existing = deepcopy(drug.get("formulations") or [])
    primary_confirmed = (drug.get("manual_review") or {}).get("primary_formulation_confirmed", False)
    if existing and not candidates:
        return existing

    if candidates:
        formulations: list[dict[str, Any]] = []
        confirmed_candidate = find_confirmed_candidate(drug) if primary_confirmed else None
        selected_any = any(candidate.get("selected") for candidate in candidates)
        for idx, candidate in enumerate(candidates):
            label = candidate.get("label") or "unknown"
            formulation_id = f"{slugify(drug['generic_name'])}-{slugify(label)}"
            if confirmed_candidate:
                is_primary = matches_manual_confirmation(candidate, drug.get("manual_review") or {})
            else:
                is_primary = bool(candidate.get("selected")) if selected_any else idx == 0
            formulations.append(
                {
                    "formulation_id": formulation_id,
                    "label": label,
                    "strength_mg": candidate.get("strength_value"),
                    "dispense_unit": candidate.get("dispense_unit") or infer_formulation_unit(label),
                    "route": candidate.get("route_hint"),
                    "is_primary": is_primary,
                    "nhi_price": candidate.get("nhi_price"),
                    "ntuh_self_pay_price": drug.get("ntuh_self_pay_price") if is_primary else None,
                    "nhi_effective_date": candidate.get("effective_start"),
                    "ntuh_query_date": (drug.get("ntuh_open_data") or {}).get("query_date") if is_primary else None,
                    "source_price_unit": label,
                    "nhi_drug_code": candidate.get("drug_code"),
                    "nhi_drug_codes": candidate.get("drug_codes") or ([candidate.get("drug_code")] if candidate.get("drug_code") else []),
                    "is_active": candidate.get("is_active"),
                    "matched_row_count": candidate.get("matched_row_count", 1),
                }
            )
        return formulations

    formulation_id = f"{slugify(drug['generic_name'])}-{infer_formulation_unit(drug.get('price_unit')) or 'unit'}"
    return [
        {
            "formulation_id": formulation_id,
            "label": drug.get("price_unit") or "unknown",
            "strength_mg": parse_strength_mg(drug.get("price_unit")),
            "dispense_unit": infer_formulation_unit(drug.get("price_unit")),
            "route": None,
            "is_primary": True,
            "nhi_price": drug.get("nhi_price"),
            "ntuh_self_pay_price": drug.get("ntuh_self_pay_price"),
            "nhi_effective_date": (drug.get("nhi_open_data") or {}).get("selected_start_date"),
            "ntuh_query_date": (drug.get("ntuh_open_data") or {}).get("query_date"),
            "source_price_unit": drug.get("price_unit"),
        }
    ]


def apply_primary_formulation_snapshot(drug: dict[str, Any]) -> None:
    formulations = drug.get("formulations") or []
    primary = next((item for item in formulations if item.get("is_primary")), None)
    if not primary and formulations:
        primary = formulations[0]
    if not primary:
        return

    if primary.get("label"):
        drug["price_unit"] = primary["label"]
    if primary.get("nhi_price") is not None:
        drug["nhi_price"] = primary["nhi_price"]
    if primary.get("nhi_drug_codes"):
        drug["nhi_drug_codes"] = list(dict.fromkeys(primary["nhi_drug_codes"]))
    elif primary.get("nhi_drug_code"):
        drug["nhi_drug_codes"] = [primary["nhi_drug_code"]]

    nhi_open_data = deepcopy(drug.get("nhi_open_data") or {})
    if primary.get("nhi_drug_code"):
        nhi_open_data["display_drug_code"] = primary["nhi_drug_code"]
    if primary.get("nhi_effective_date"):
        nhi_open_data["display_start_date"] = primary["nhi_effective_date"]
    drug["nhi_open_data"] = nhi_open_data


def confirm_primary_formulation(
    drug: dict[str, Any],
    *,
    confirmed_drug_code: str | None = None,
    confirmed_formulation_label: str | None = None,
    verified_by: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    manual_review = deepcopy(drug.get("manual_review") or {})
    confirmed_at = datetime.now().isoformat(timespec="seconds")
    manual_review["primary_formulation_confirmed"] = True
    if confirmed_drug_code:
        manual_review["confirmed_drug_code"] = confirmed_drug_code
    if confirmed_formulation_label:
        manual_review["confirmed_formulation_label"] = confirmed_formulation_label
    manual_review["last_verified_at"] = confirmed_at
    if verified_by:
        manual_review["verified_by"] = verified_by
    if note:
        existing_note = (manual_review.get("notes") or "").strip()
        manual_review["notes"] = f"{existing_note}\n{note}".strip() if existing_note else note
    checked_fields = list(dict.fromkeys([*(manual_review.get("checked_fields") or []), "formulation", "nhi_price"]))
    manual_review["checked_fields"] = checked_fields
    manual_review["canonical_decision"] = "confirmed"
    drug["manual_review"] = manual_review
    record_versions = deepcopy(drug.get("record_versions") or [])
    record_versions.append(
        {
            "version": f"manual-lock-{confirmed_at}",
            "event_type": "formulation_confirmed",
            "event_at": confirmed_at,
            "summary": (
                f"人工確認主劑型為 {confirmed_formulation_label or '未指定標籤'}"
                + (f"（{confirmed_drug_code}）" if confirmed_drug_code else "")
            ),
            "source": verified_by or "manual",
        }
    )
    drug["record_versions"] = record_versions
    return attach_catalog_scaffold(drug)


def add_recommendation_source_version(
    drug: dict[str, Any],
    *,
    source_type: str,
    source_name: str,
    category: str,
    recommendation: str,
    effective_or_query_date: str | None = None,
    evidence_note: str = "",
    reference_codes: list[str] | None = None,
    source_url: str | None = None,
    verified_by: str | None = None,
) -> dict[str, Any]:
    source_id = slugify(f"{source_type}-{source_name}-{category}")
    sources = [normalize_recommendation_source(item) for item in (drug.get("recommendation_sources") or [])]
    version = make_source_version(
        source_id=source_id,
        date_value=effective_or_query_date,
        recommendation=recommendation,
        evidence_note=evidence_note,
        reference_codes=reference_codes or [],
        source_url=source_url,
    )
    existing = next(
        (
            item
            for item in sources
            if item.get("source_type") == source_type
            and item.get("source_name") == source_name
            and item.get("category") == category
        ),
        None,
    )
    if existing is None:
        sources.append(
            {
                "source_id": source_id,
                "source_type": source_type,
                "source_name": source_name,
                "category": category,
                "versions": [version],
            }
        )
    else:
        existing.setdefault("versions", []).append(version)
    drug["recommendation_sources"] = sources

    event_at = datetime.now().isoformat(timespec="seconds")
    record_versions = deepcopy(drug.get("record_versions") or [])
    record_versions.append(
        {
            "version": f"source-version-{event_at}",
            "event_type": "recommendation_source_added",
            "event_at": event_at,
            "summary": f"新增 {source_name} 來源版本：{recommendation}",
            "source": verified_by or source_type,
        }
    )
    drug["record_versions"] = record_versions
    return attach_catalog_scaffold(drug)


def seed_dosing_profiles(drug: dict[str, Any]) -> list[dict[str, Any]]:
    if drug.get("dosing_profiles"):
        return deepcopy(drug["dosing_profiles"])

    raw = drug.get("dosage_info")
    if not raw:
        return []
    parsed = json.loads(raw) if isinstance(raw, str) else deepcopy(raw)
    schedule = normalize_schedule(parsed.get("schedule"))
    if parsed.get("dose_per_bsa") is not None:
        mode = "bsa"
        dose_value = parsed.get("dose_per_bsa")
        dose_unit = parsed.get("unit", "mg/m2")
    elif parsed.get("dose_per_kg") is not None:
        mode = "weight"
        dose_value = parsed.get("dose_per_kg")
        dose_unit = parsed.get("unit", "mg/kg")
    else:
        mode = "fixed_daily"
        dose_value = parsed.get("dose_fixed")
        dose_unit = parsed.get("unit", "mg")

    profile = {
        "profile_id": "default",
        "display_name": "標準常用劑量",
        "dose_mode": mode,
        "dose_value": dose_value,
        "dose_unit": dose_unit,
        "frequency": parsed.get("freq"),
        "route": parsed.get("type"),
        "note": parsed.get("note"),
        "days_on": schedule.get("days_on") if schedule else None,
        "cycle_days": schedule.get("cycle_days") if schedule else None,
        "max_dose_mg": parsed.get("max_dose"),
    }
    return [profile]


def seed_regimen_refs(drug: dict[str, Any]) -> list[str]:
    current = drug.get("common_regimen_refs")
    if current:
        return list(dict.fromkeys(current))
    return REGIMEN_GENERIC_MAP.get(drug["generic_name"], [])


def infer_diseases_from_text(*texts: str | None) -> list[str]:
    haystack = " ".join(text for text in texts if text).casefold()
    inferred: list[str] = []
    for disease, keywords in DISEASE_KEYWORDS:
        if any(keyword.casefold() in haystack for keyword in keywords):
            inferred.append(disease)
    return inferred


def seed_disease_inference(drug: dict[str, Any]) -> dict[str, Any]:
    current = deepcopy(drug.get("disease_inference") or {})
    inferred = infer_diseases_from_text(
        drug.get("indication"),
        drug.get("conditions"),
        drug.get("nhi_rule_text"),
    )
    tags = drug.setdefault("clinical_tags", {})
    existing = list(dict.fromkeys(tags.get("disease") or []))
    if not existing and inferred:
        tags["disease"] = inferred
    confirmed = current.get("confirmed", False)
    return {
        "source": current.get("source", "nhi_rule_text"),
        "inferred_diseases": inferred,
        "confirmed": confirmed,
        "requires_confirmation": False if confirmed else bool(inferred),
        "last_inferred_at": datetime.now().isoformat(timespec="seconds"),
    }


def make_source_version(
    *,
    source_id: str,
    date_value: str | None,
    recommendation: str,
    evidence_note: str,
    reference_codes: list[str] | None = None,
    source_url: str | None = None,
) -> dict[str, Any]:
    suffix = re.sub(r"[^0-9A-Za-z]+", "-", date_value or "undated").strip("-") or "undated"
    return {
        "version_id": f"{source_id}-{suffix}",
        "effective_or_query_date": date_value,
        "recommendation": recommendation,
        "evidence_note": evidence_note,
        "reference_codes": reference_codes or [],
        "source_url": source_url,
    }


def normalize_recommendation_source(item: dict[str, Any]) -> dict[str, Any]:
    source_id = item.get("source_id") or slugify(f"{item.get('source_type', 'source')}-{item.get('source_name', 'unknown')}-{item.get('category', 'general')}")
    if item.get("versions"):
        versions = deepcopy(item["versions"])
    else:
        versions = [
            make_source_version(
                source_id=source_id,
                date_value=item.get("effective_or_query_date"),
                recommendation=item.get("recommendation") or "未提供建議",
                evidence_note=item.get("evidence_note") or "",
                reference_codes=[code for code in (item.get("reference_codes") or []) if code],
                source_url=item.get("source_url"),
            )
        ]
    return {
        "source_id": source_id,
        "source_type": item.get("source_type") or "Pending",
        "source_name": item.get("source_name") or "待確認來源",
        "category": item.get("category") or "general",
        "versions": versions,
    }


def seed_recommendation_sources(drug: dict[str, Any]) -> list[dict[str, Any]]:
    seeded = [normalize_recommendation_source(item) for item in (drug.get("recommendation_sources") or [])]

    def upsert_source(
        *,
        source_id: str,
        source_type: str,
        source_name: str,
        category: str,
        version: dict[str, Any],
    ) -> None:
        existing = next(
            (
                item
                for item in seeded
                if item.get("source_type") == source_type
                and item.get("source_name") == source_name
                and item.get("category") == category
            ),
            None,
        )
        if not existing:
            seeded.append(
                {
                    "source_id": source_id,
                    "source_type": source_type,
                    "source_name": source_name,
                    "category": category,
                    "versions": [version],
                }
            )
            return
        signature = (
            version.get("effective_or_query_date"),
            version.get("recommendation"),
            tuple(version.get("reference_codes") or []),
        )
        existing_signatures = {
            (
                item.get("effective_or_query_date"),
                item.get("recommendation"),
                tuple(item.get("reference_codes") or []),
            )
            for item in (existing.get("versions") or [])
        }
        if signature not in existing_signatures:
            existing.setdefault("versions", []).append(version)

    therapy_line = drug.get("therapy_line")
    therapy_line_source = drug.get("therapy_line_source") or "待確認"
    pay_codes = [code for code in (drug.get("nhi_pay_codes") or []) if code]
    if therapy_line_source == "健保規定":
        source_type = "NHI"
        source_name = "健保給付規定"
        source_id = "nhi-coverage-line"
        recommendation = f"目前主檔標示為第 {therapy_line} 線，依健保給付規定整理。"
        evidence_note = (
            f"給付規定章節：{'、'.join(pay_codes)}。實際條件仍應逐條核對事前審查與前置治療要求。"
            if pay_codes
            else "目前未帶出給付規定章節，需另行核對原始條文。"
        )
    elif therapy_line_source == "NCCN":
        source_type = "NCCN"
        source_name = "NCCN Guideline"
        source_id = "nccn-therapy-line"
        recommendation = f"目前主檔標示為第 {therapy_line} 線，但此線別來自指引推估，非健保條文明示。"
        evidence_note = "若要申報健保，仍需回到最新健保條文確認是否明列先前治療條件。"
    else:
        source_type = "Pending"
        source_name = "待確認"
        source_id = "pending-therapy-line"
        recommendation = "目前治療線尚未確認，需人工判讀條文或指引。"
        evidence_note = "本欄暫無足夠證據自動判定第幾線。"

    upsert_source(
        source_id=source_id,
        source_type=source_type,
        source_name=source_name,
        category="coverage_line",
        version=make_source_version(
            source_id=source_id,
            date_value=(drug.get("nhi_open_data") or {}).get("display_start_date")
            or (drug.get("nhi_open_data") or {}).get("selected_start_date"),
            recommendation=recommendation,
            evidence_note=evidence_note,
            reference_codes=pay_codes,
        ),
    )

    if (drug.get("ntuh_open_data") or {}).get("source_url"):
        upsert_source(
            source_id="ntuh-self-pay",
            source_type="NTUH",
            source_name="台大醫院院內資料",
            category="self_pay_pricing",
            version=make_source_version(
                source_id="ntuh-self-pay",
                date_value=(drug.get("ntuh_open_data") or {}).get("query_date"),
                recommendation="目前僅提供院內自費價與頁面健保價參考，不作為第幾線治療建議依據。",
                evidence_note="台大查詢頁面未提供本系統可直接結構化擷取的治療線條件。",
                reference_codes=[code for code in [(drug.get("ntuh_open_data") or {}).get("selected_code")] if code],
                source_url=(drug.get("ntuh_open_data") or {}).get("source_url"),
            ),
        )

    return seeded


def attach_catalog_scaffold(drug: dict[str, Any]) -> dict[str, Any]:
    drug["manual_review"] = seed_manual_review(drug)
    drug["record_versions"] = seed_record_versions(drug)
    drug["formulations"] = seed_formulations(drug)
    apply_primary_formulation_snapshot(drug)
    drug["dosing_profiles"] = seed_dosing_profiles(drug)
    drug["common_regimen_refs"] = seed_regimen_refs(drug)
    drug["disease_inference"] = seed_disease_inference(drug)
    drug["recommendation_sources"] = seed_recommendation_sources(drug)
    current_rules = deepcopy(drug.get("formulation_review_rules") or {})
    requires_manual_confirmation = drug["manual_review"].get("multi_formulation_pending", False)
    drug["formulation_review_rules"] = {
        "requires_manual_confirmation": requires_manual_confirmation,
        "rule_summary": (
            f"同成分存在 {drug['manual_review'].get('candidate_formulation_count', 0)} 個官方候選劑型，"
            "需人工指定主劑型、藥品代碼與價格來源。"
            if requires_manual_confirmation
            else "目前僅有單一主要劑型，可直接沿用主檔。"
        ),
        "checks": current_rules.get("checks") or [
            "確認主劑型 strength 與實際臨床常用品項一致",
            "確認健保價是否對應正確劑量與藥證",
            "確認台大院內價是否為同一 strength，而非不同包裝",
            "若官方回傳 0.00，需人工判定是否為停用、未收載或資料異常",
        ],
    }
    drug["issue_tracking"] = deepcopy(drug.get("issue_tracking") or {
        "pending_count": 0,
        "has_pending_error": False,
        "latest_reported_at": None,
        "open_issue_urls": [],
    })
    drug["catalog_meta"] = {
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "supports_multi_formulation": True,
        "supports_regimen_costing": True,
        "supports_manual_verification": True,
        "supports_specialty_bootstrap": True,
        "primary_formulation_source": "manual" if drug["manual_review"].get("primary_formulation_confirmed") else "auto",
        "primary_formulation_label": drug.get("price_unit"),
        "primary_nhi_drug_code": (drug.get("nhi_open_data") or {}).get("display_drug_code"),
    }
    return drug


def build_drug_template(
    generic_name: str,
    trade_names: str | None = None,
    specialty_id: str = "oncology_heme",
) -> dict[str, Any]:
    new_id = int(math.floor(datetime.now().timestamp()))
    template: dict[str, Any] = {
        "id": new_id,
        "generic_name": generic_name,
        "trade_names": trade_names,
        "specialty_id": specialty_id,
        "indication": "",
        "clinical_tags": {"disease": [], "phase": []},
        "stage": "",
        "therapy_line": 1,
        "prior_auth": False,
        "conditions": "",
        "nhi_price": None,
        "price_unit": None,
        "dosage_info": None,
        "therapy_line_source": "待確認",
        "nhi_open_data": {},
        "nhi_drug_codes": [],
        "nhi_pay_codes": [],
        "nhi_pay_pdf_urls": [],
        "nhi_pay_pdf_filenames": [],
        "ntuh_self_pay_price": None,
        "ntuh_price_unit": None,
        "ntuh_open_data": {},
    }
    return attach_catalog_scaffold(template)
