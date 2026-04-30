from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qs, urlparse

import fitz
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATASET_IDENTIFIER = "A21030000I-E41001"
RESOURCE_ID = "A21030000I-E41001-001"
DATASET_META_URL = f"https://info.nhi.gov.tw/api/iode0010/v1/rest/dataset/{DATASET_IDENTIFIER}"
DATASET_DUMP_URL = f"https://info.nhi.gov.tw/api/iode0010/v1/dump/datastore/{RESOURCE_ID}?format=CSV"

FORM_UNIT_HINTS = {
    "膠囊": "cap",
    "軟膠囊": "cap",
    "膜衣錠": "tab",
    "糖衣錠": "tab",
    "錠": "tab",
    "注射劑": "vial",
    "凍晶注射劑": "vial",
    "注射液": "vial",
    "粉末": "vial",
}


@dataclass
class OfficialRow:
    raw: dict[str, str]
    ingredient_norm: str
    drug_name_norm: str
    trade_name_norm: str
    pay_codes: list[str]
    pay_urls: list[str]
    pay_files: list[str]
    start_date_int: int
    end_date_int: int
    is_active: bool


def load_json_records(path: str | Path) -> list[dict[str, Any]]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json_records(path: str | Path, data: list[dict[str, Any]]) -> None:
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    value = value.upper().strip()
    value = re.sub(r"[^A-Z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def split_trade_names(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in re.split(r"[／/]|,|;", value) if part.strip()]


def parse_numeric_date(value: str | None) -> int:
    digits = re.sub(r"\D", "", value or "")
    if not digits:
        return 0
    return int(digits)


def current_roc_date() -> int:
    now = datetime.now()
    return int(f"{now.year - 1911:03d}{now.month:02d}{now.day:02d}")


def parse_price(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


def parse_strength_token(price_unit: str | None) -> str:
    if not price_unit:
        return ""
    normalized = price_unit.upper().replace("²", "2")
    match = re.search(r"(\d+(?:\.\d+)?)\s*(MG(?:/ML|/M2)?|MCG|G|IU|U)", normalized)
    if not match:
        return ""
    return f"{match.group(1)} {match.group(2)}"


def price_unit_hint(price_unit: str | None) -> str:
    if not price_unit:
        return ""
    unit = price_unit.lower()
    if "cap" in unit:
        return "cap"
    if "tab" in unit:
        return "tab"
    if "vial" in unit:
        return "vial"
    return ""


def infer_form_hint(drug_form: str) -> str:
    for needle, unit in FORM_UNIT_HINTS.items():
        if needle in drug_form:
            return unit
    return ""


def parse_strength_value_and_unit(text: str | None) -> tuple[float | None, str | None]:
    if not text:
        return None, None
    match = re.search(r"(\d+(?:\.\d+)?)\s*(MG|MCG|G|IU|U)", text, flags=re.I)
    if not match:
        return None, None
    return float(match.group(1)), match.group(2).lower()


def parse_spec_amount_and_unit(amount: str | None, unit: str | None) -> tuple[float | None, str | None]:
    if not amount and not unit:
        return None, None
    try:
        numeric = float(str(amount).strip())
    except ValueError:
        return None, (unit or "").strip().lower() or None
    return numeric, (unit or "").strip().lower() or None


def format_strength_label(value: float | None, unit: str | None) -> str:
    if value is None or not unit:
        return ""
    normalized = {
        "gm": "g",
        "gram": "g",
        "grams": "g",
        "ml": "ml",
        "mcg": "mcg",
        "mg": "mg",
        "iu": "iu",
        "u": "u",
    }.get(unit.lower(), unit.lower())
    return f"{value:g}{normalized.upper()}"


def filename_from_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    return parse_qs(parsed.query).get("DurgFileName", [""])[0]


def extract_pdf_version(filename: str) -> str | None:
    match = re.search(r"_(\d{8})", filename)
    return match.group(1) if match else None


def official_rows_from_csv(csv_text: str) -> list[OfficialRow]:
    today = current_roc_date()
    rows: list[OfficialRow] = []
    reader = csv.DictReader(io.StringIO(csv_text))
    for raw_row in reader:
        pay_codes = [code.strip() for code in (raw_row.get("給付規定章節") or "").split(",") if code.strip()]
        pay_urls = [url.strip() for url in (raw_row.get("給付規定章節連結") or "").split(",") if url.strip()]
        pay_files = [filename_from_url(url) for url in pay_urls if filename_from_url(url)]
        start_date_int = parse_numeric_date(raw_row.get("有效起日"))
        end_date_int = parse_numeric_date(raw_row.get("有效迄日")) or 9991231
        rows.append(
            OfficialRow(
                raw=raw_row,
                ingredient_norm=normalize_text(raw_row.get("成分")),
                drug_name_norm=normalize_text(raw_row.get("藥品英文名稱")),
                trade_name_norm=normalize_text(raw_row.get("藥品中文名稱")),
                pay_codes=pay_codes,
                pay_urls=pay_urls,
                pay_files=pay_files,
                start_date_int=start_date_int,
                end_date_int=end_date_int,
                is_active=start_date_int <= today <= end_date_int,
            )
        )
    return rows


class NhiOpenDataUpdater:
    def __init__(self, verify_ssl: bool = False, timeout_meta: int = 60, timeout_dump: int = 180):
        self.verify_ssl = verify_ssl
        self.timeout_meta = timeout_meta
        self.timeout_dump = timeout_dump
        self.session = requests.Session()

    def fetch_dataset(self) -> tuple[dict[str, Any], list[OfficialRow]]:
        metadata = self.session.get(DATASET_META_URL, timeout=self.timeout_meta, verify=self.verify_ssl).json()
        response = self.session.get(DATASET_DUMP_URL, timeout=self.timeout_dump, verify=self.verify_ssl)
        response.raise_for_status()
        archive = zipfile.ZipFile(io.BytesIO(response.content))
        csv_name = archive.namelist()[0]
        csv_text = archive.read(csv_name).decode("utf-8-sig")
        return metadata, official_rows_from_csv(csv_text)

    @staticmethod
    def latest_per_drug_code(rows: list[OfficialRow]) -> list[OfficialRow]:
        latest: dict[str, OfficialRow] = {}
        for row in rows:
            code = row.raw["藥品代號"]
            prior = latest.get(code)
            if prior is None or row.start_date_int >= prior.start_date_int:
                latest[code] = row
        return list(latest.values())

    @staticmethod
    def rows_for_generic_name(generic_name: str, rows: list[OfficialRow]) -> list[OfficialRow]:
        generic_norm = normalize_text(generic_name)
        matched = [
            row
            for row in rows
            if row.ingredient_norm == generic_norm or row.ingredient_norm.startswith(f"{generic_norm} ")
        ]
        return NhiOpenDataUpdater.latest_per_drug_code(matched)

    @staticmethod
    def choose_price_row(drug: dict[str, Any], rows: list[OfficialRow]) -> tuple[OfficialRow | None, str]:
        if not rows:
            return None, "no-match"

        active_rows = [row for row in rows if row.is_active]
        candidates = active_rows or rows
        confidence = "single-active" if len(candidates) == 1 else "multiple-active"

        strength_token = parse_strength_token(drug.get("price_unit"))
        if strength_token:
            strength_matches = [row for row in candidates if strength_token in normalize_text(row.raw.get("成分"))]
            if strength_matches:
                candidates = strength_matches
                confidence = "exact-strength"

        trade_names = [normalize_text(name) for name in split_trade_names(drug.get("trade_names"))]
        if trade_names:
            trade_matches = []
            for row in candidates:
                haystacks = [row.drug_name_norm, row.trade_name_norm]
                if any(
                    trade_name and any(trade_name in haystack for haystack in haystacks)
                    for trade_name in trade_names
                ):
                    trade_matches.append(row)
            if trade_matches:
                candidates = trade_matches
                confidence = "trade-name"

        unit_hint = price_unit_hint(drug.get("price_unit"))
        if unit_hint:
            form_matches = [
                row
                for row in candidates
                if infer_form_hint(row.raw.get("劑型", "")) in {"", unit_hint}
            ]
            if form_matches:
                candidates = form_matches

        if len(candidates) > 1 and drug.get("nhi_price") is not None:
            existing = parse_price(str(drug["nhi_price"]))
            if existing is not None:
                candidates = sorted(
                    candidates,
                    key=lambda row: abs((parse_price(row.raw.get("支付價")) or existing) - existing),
                )

        candidates = sorted(
            candidates,
            key=lambda row: (row.start_date_int, parse_price(row.raw.get("支付價")) or 0),
            reverse=True,
        )
        return candidates[0], confidence

    @staticmethod
    def extract_pdf_text(pdf_path: Path) -> str:
        doc = fitz.open(pdf_path)
        try:
            text = "\n".join(page.get_text() for page in doc)
        finally:
            doc.close()

        cleaned_lines: list[str] = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if re.fullmatch(r"\(\d{3,4}\.\d{1,2}\.\d{1,2}更新\)", line):
                continue
            if re.fullmatch(r"\d{1,4}", line):
                continue
            cleaned_lines.append(line)
        return "\n".join(cleaned_lines).strip()

    def download_pdf(self, url: str, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        response = self.session.get(url, timeout=120, verify=self.verify_ssl)
        response.raise_for_status()
        target.write_bytes(response.content)

    @staticmethod
    def should_update(drug: dict[str, Any], selected_names: set[str]) -> bool:
        if not selected_names:
            return True
        return normalize_text(drug["generic_name"]) in selected_names

    def update_drug(
        self,
        drug: dict[str, Any],
        official_rows: list[OfficialRow],
        dataset_meta: dict[str, Any],
        skip_pdf: bool = False,
        pdf_cache_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        matches = self.rows_for_generic_name(drug["generic_name"], official_rows)
        selected_row, confidence = self.choose_price_row(drug, matches)

        pay_codes = sorted({code for row in matches for code in row.pay_codes})
        pdf_pairs: list[tuple[str, str]] = []
        seen_pairs: set[tuple[str, str]] = set()
        for row in matches:
            for pay_code, pay_url in zip(row.pay_codes, row.pay_urls):
                filename = filename_from_url(pay_url)
                pair = (pay_url, filename)
                if not pay_code or not filename or pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                pdf_pairs.append(pair)

        pay_urls = [url for url, _ in pdf_pairs]
        pay_files = [filename for _, filename in pdf_pairs]
        rule_versions = sorted({version for version in (extract_pdf_version(name) for name in pay_files) if version})

        pdf_cache_paths: list[str] = []
        rule_texts: list[tuple[str, str]] = []
        if not skip_pdf and pdf_cache_dir:
            pdf_root = Path(pdf_cache_dir).resolve()
            for url, filename in pdf_pairs:
                target = pdf_root / filename
                if not target.exists():
                    self.download_pdf(url, target)
                pdf_cache_paths.append(str(target))
                rule_texts.append((filename, self.extract_pdf_text(target)))

        selected_price = parse_price(selected_row.raw.get("支付價")) if selected_row else None
        formulation_candidates = self.build_formulation_candidates(matches)
        if selected_row:
            for candidate in formulation_candidates:
                candidate["selected"] = candidate.get("drug_code") == selected_row.raw.get("藥品代號")

        drug["nhi_open_data"] = {
            "dataset_identifier": DATASET_IDENTIFIER,
            "dataset_resource_id": RESOURCE_ID,
            "dataset_modified": dataset_meta.get("modified"),
            "matched_rows_count": len(matches),
            "selected_confidence": confidence,
            "selected_drug_code": selected_row.raw.get("藥品代號") if selected_row else None,
            "selected_drug_name": selected_row.raw.get("藥品英文名稱") if selected_row else None,
            "selected_start_date": selected_row.raw.get("有效起日") if selected_row else None,
            "selected_end_date": selected_row.raw.get("有效迄日") if selected_row else None,
            "pay_codes": pay_codes,
            "pay_pdf_filenames": pay_files,
            "pay_pdf_urls": pay_urls,
            "pay_pdf_versions": rule_versions,
            "pdf_cache_paths": pdf_cache_paths,
            "last_synced_at": datetime.now().isoformat(timespec="seconds"),
        }
        drug["nhi_drug_codes"] = sorted({row.raw["藥品代號"] for row in matches})
        drug["nhi_formulation_candidates"] = formulation_candidates
        drug["nhi_pay_codes"] = pay_codes
        drug["nhi_pay_pdf_urls"] = pay_urls
        drug["nhi_pay_pdf_filenames"] = pay_files

        if rule_versions:
            drug["nhi_pay_last_updated"] = rule_versions[-1]
        if rule_texts:
            drug["nhi_rule_text"] = "\n\n".join(f"[{filename}]\n{text}" for filename, text in rule_texts if text).strip()
        if selected_price is not None and confidence in {"exact-strength", "trade-name", "single-active"}:
            drug["nhi_price"] = selected_price
        return drug

    @staticmethod
    def build_formulation_candidates(rows: list[OfficialRow]) -> list[dict[str, Any]]:
        grouped: dict[str, dict[str, Any]] = {}
        for row in sorted(rows, key=lambda item: (item.start_date_int, item.raw.get("藥品代號", "")), reverse=True):
            spec_amount = (row.raw.get("規格量") or "").strip()
            spec_unit = (row.raw.get("規格單位") or "").strip()
            form_hint = infer_form_hint(row.raw.get("劑型", ""))
            strength_value, strength_unit = parse_strength_value_and_unit(row.raw.get("成分") or row.raw.get("藥品英文名稱"))
            spec_value, spec_unit_norm = parse_spec_amount_and_unit(spec_amount, spec_unit)

            total_strength_value = strength_value
            if spec_value and spec_unit_norm == "ml" and strength_value and strength_unit == "mg":
                total_strength_value = strength_value * spec_value

            strength_label = format_strength_label(total_strength_value, strength_unit)
            spec_label = format_strength_label(spec_value, spec_unit_norm)

            if spec_value and spec_unit_norm == "ml" and strength_label:
                label = f"{strength_label}/{spec_amount}{spec_unit.upper()}/{form_hint or 'unit'}"
            elif strength_label and spec_label and strength_label == spec_label:
                label = f"{strength_label}/{form_hint or 'unit'}"
            elif strength_label and spec_label:
                label = f"{strength_label}/{spec_label}/{form_hint or 'unit'}"
            elif strength_value and strength_unit and form_hint:
                label = f"{strength_value:g}{strength_unit.upper()}/{form_hint}"
            elif spec_amount or spec_unit:
                label = f"{spec_amount}{spec_unit}".strip()
                if label and form_hint:
                    label = f"{label}/{form_hint}"
            else:
                label = row.raw.get("藥品英文名稱") or row.raw.get("藥品代號") or "unknown"

            entry = grouped.get(label)
            if not entry:
                grouped[label] = {
                    "drug_code": row.raw.get("藥品代號"),
                    "drug_codes": [row.raw.get("藥品代號")] if row.raw.get("藥品代號") else [],
                    "english_name": row.raw.get("藥品英文名稱"),
                    "chinese_name": row.raw.get("藥品中文名稱"),
                    "label": label,
                    "strength_value": total_strength_value,
                    "strength_unit": strength_unit,
                    "dispense_unit": form_hint or None,
                    "route_hint": row.raw.get("劑型"),
                    "nhi_price": parse_price(row.raw.get("支付價")),
                    "effective_start": row.raw.get("有效起日"),
                    "effective_end": row.raw.get("有效迄日"),
                    "is_active": row.is_active,
                    "selected": False,
                    "matched_row_count": 1,
                }
                continue

            entry["matched_row_count"] += 1
            code = row.raw.get("藥品代號")
            if code and code not in entry["drug_codes"]:
                entry["drug_codes"].append(code)
            if row.is_active and not entry.get("is_active"):
                entry["is_active"] = True
            if row.start_date_int > parse_numeric_date(entry.get("effective_start")):
                entry["drug_code"] = row.raw.get("藥品代號")
                entry["english_name"] = row.raw.get("藥品英文名稱")
                entry["chinese_name"] = row.raw.get("藥品中文名稱")
                entry["route_hint"] = row.raw.get("劑型")
                entry["nhi_price"] = parse_price(row.raw.get("支付價"))
                entry["effective_start"] = row.raw.get("有效起日")
                entry["effective_end"] = row.raw.get("有效迄日")

        return list(grouped.values())

    def update_records(
        self,
        records: list[dict[str, Any]],
        selected_drugs: Iterable[str] | None = None,
        skip_pdf: bool = False,
        pdf_cache_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        selected_names = {normalize_text(name) for name in (selected_drugs or [])}
        dataset_meta, official_rows = self.fetch_dataset()
        updated = 0
        for drug in records:
            if not self.should_update(drug, selected_names):
                continue
            self.update_drug(
                drug,
                official_rows=official_rows,
                dataset_meta=dataset_meta,
                skip_pdf=skip_pdf,
                pdf_cache_dir=pdf_cache_dir,
            )
            updated += 1
        return {
            "updated_drugs": updated,
            "dataset_identifier": DATASET_IDENTIFIER,
            "resource_id": RESOURCE_ID,
            "dataset_modified": dataset_meta.get("modified"),
        }

    def update_file(
        self,
        data_path: str | Path,
        output_path: str | Path | None = None,
        selected_drugs: Iterable[str] | None = None,
        skip_pdf: bool = False,
        pdf_cache_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        records = load_json_records(data_path)
        result = self.update_records(
            records,
            selected_drugs=selected_drugs,
            skip_pdf=skip_pdf,
            pdf_cache_dir=pdf_cache_dir,
        )
        final_output = Path(output_path) if output_path else Path(data_path)
        save_json_records(final_output, records)
        result["output"] = str(final_output.resolve())
        return result
