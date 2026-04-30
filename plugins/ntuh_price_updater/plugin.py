from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://dept.ntuh.gov.tw/phar/WebAp/QueryDrugInfoPhr.aspx"
FREE_MARKERS = ("<專>(FREE)", "<試>")


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


def split_trade_names(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in re.split(r"[/,;]| OR ", value, flags=re.I) if part.strip()]


def parse_numeric_price(text: str | None) -> float | None:
    if not text:
        return None
    digits = re.sub(r"[^\d.]+", "", text)
    if not digits:
        return None
    try:
        return float(digits)
    except ValueError:
        return None


class NtuhPriceUpdater:
    def __init__(self, verify_ssl: bool = False, timeout: int = 30):
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.session = requests.Session()

    @staticmethod
    def should_update(drug: dict[str, Any], selected_names: set[str]) -> bool:
        if not selected_names:
            return True
        return normalize_text(drug["generic_name"]) in selected_names

    @staticmethod
    def get_tokens(soup: BeautifulSoup) -> dict[str, str]:
        def value(field_id: str) -> str:
            element = soup.find("input", {"id": field_id})
            return element["value"] if element else ""

        return {
            "__VIEWSTATE": value("__VIEWSTATE"),
            "__VIEWSTATEGENERATOR": value("__VIEWSTATEGENERATOR"),
            "__EVENTVALIDATION": value("__EVENTVALIDATION"),
        }

    @staticmethod
    def extract_span_text(soup: BeautifulSoup, pattern: str) -> str:
        element = soup.find("span", {"id": re.compile(pattern)})
        return element.get_text(strip=True) if element else ""

    @staticmethod
    def infer_display_unit(drug: dict[str, Any]) -> str:
        return drug.get("price_unit") or ""

    @staticmethod
    def make_search_terms(drug: dict[str, Any]) -> list[str]:
        terms: list[str] = []
        for part in split_trade_names(drug.get("trade_names")):
            if part and part not in terms:
                terms.append(part)
        generic = drug["generic_name"].strip()
        if generic and generic not in terms:
            terms.append(generic)
        return terms

    def search_drug(self, search_name: str) -> list[dict[str, str]]:
        response = self.session.get(BASE_URL, verify=self.verify_ssl, timeout=self.timeout)
        response.raise_for_status()
        tokens = self.get_tokens(BeautifulSoup(response.content, "html.parser"))

        response = self.session.post(
            BASE_URL,
            verify=self.verify_ssl,
            timeout=self.timeout,
            data={
                **tokens,
                "DrugInfoQueryBox$txbDrugName": search_name,
                "DrugInfoQueryBox$btnQueryByDrugName": "查詢",
            },
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        tokens = self.get_tokens(soup)

        results: list[dict[str, str]] = []
        for table in soup.find_all("table"):
            if "八碼" not in table.get_text():
                continue
            for row in table.find_all("tr"):
                columns = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
                if len(columns) < 4:
                    continue
                code = columns[1].strip()
                if not re.fullmatch(r"[A-Z0-9 ]{6,9}", code):
                    continue
                link = row.find("a", href=re.compile(r"btnGenericName"))
                if not link:
                    continue
                postback = re.search(r"__doPostBack\('([^']+)','([^']*)'\)", link["href"])
                if not postback:
                    continue
                results.append(
                    {
                        "code": code,
                        "generic": columns[0],
                        "chinese": columns[2],
                        "product": columns[3],
                        "event_target": postback.group(1),
                        "event_argument": postback.group(2),
                        "search_term": search_name,
                        **tokens,
                    }
                )
            break
        return results

    def get_detail(self, entry: dict[str, str]) -> dict[str, str]:
        response = self.session.post(
            BASE_URL,
            verify=self.verify_ssl,
            timeout=self.timeout,
            data={
                "__VIEWSTATE": entry["__VIEWSTATE"],
                "__VIEWSTATEGENERATOR": entry["__VIEWSTATEGENERATOR"],
                "__EVENTVALIDATION": entry["__EVENTVALIDATION"],
                "__EVENTTARGET": entry["event_target"],
                "__EVENTARGUMENT": entry["event_argument"],
            },
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return {
            "ntuh_nhi_price_text": self.extract_span_text(soup, r"lblNHIPrice"),
            "ntuh_self_pay_price_text": self.extract_span_text(soup, r"lblPatientOwnPrice"),
            "side_effects": self.extract_span_text(soup, r"lblSideEffect"),
            "contraindications": self.extract_span_text(soup, r"lblContraindications"),
            "notes": self.extract_span_text(soup, r"lblNote"),
        }

    @staticmethod
    def pick_best_candidate(drug: dict[str, Any], candidates: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str]:
        if not candidates:
            return None, "no-match"

        trade_names = [normalize_text(name) for name in split_trade_names(drug.get("trade_names"))]
        generic_norm = normalize_text(drug["generic_name"])
        strength_token = parse_strength_token(drug.get("price_unit"))
        unit_hint = price_unit_hint(drug.get("price_unit"))

        scored: list[tuple[tuple[int, int, int, int, int], dict[str, Any]]] = []
        for candidate in candidates:
            haystack = " ".join(
                [
                    candidate.get("generic", ""),
                    candidate.get("chinese", ""),
                    candidate.get("product", ""),
                    candidate.get("search_term", ""),
                ]
            )
            normalized = normalize_text(haystack)
            has_self_pay = 1 if (candidate.get("ntuh_self_pay_price") or 0) > 0 else 0
            not_free = 0 if any(marker in candidate.get("product", "").upper() for marker in FREE_MARKERS) else 1
            trade_score = 1 if any(name and name in normalized for name in trade_names) else 0
            generic_score = 1 if generic_norm and generic_norm in normalized else 0
            strength_score = 1 if strength_token and strength_token in normalized else 0
            unit_score = 1 if unit_hint and unit_hint in normalized else 0
            scored.append(((has_self_pay, not_free, trade_score + generic_score, strength_score, unit_score), candidate))

        scored.sort(key=lambda item: item[0], reverse=True)
        best = scored[0][1]
        confidence = "matched"
        if scored[0][0][0] == 0:
            confidence = "no-self-pay"
        elif scored[0][0][3] == 1:
            confidence = "exact-strength"
        elif scored[0][0][2] > 0:
            confidence = "trade-or-generic"
        return best, confidence

    def update_drug(self, drug: dict[str, Any]) -> None:
        candidates: list[dict[str, Any]] = []
        for term in self.make_search_terms(drug):
            for result in self.search_drug(term):
                detail = self.get_detail(result)
                merged = {
                    **result,
                    **detail,
                    "ntuh_self_pay_price": parse_numeric_price(detail.get("ntuh_self_pay_price_text")),
                }
                merged["ntuh_nhi_price_numeric"] = parse_numeric_price(detail.get("ntuh_nhi_price_text"))
                candidates.append(merged)

        unique_candidates: dict[tuple[str, str], dict[str, Any]] = {}
        for candidate in candidates:
            key = (candidate["code"], candidate.get("product", ""))
            existing = unique_candidates.get(key)
            if existing is None or (candidate.get("ntuh_self_pay_price") or 0) > (existing.get("ntuh_self_pay_price") or 0):
                unique_candidates[key] = candidate

        selected, confidence = self.pick_best_candidate(drug, list(unique_candidates.values()))
        query_date = datetime.now().strftime("%Y-%m-%d")
        last_synced_at = datetime.now().isoformat(timespec="seconds")

        drug["ntuh_self_pay_price"] = selected.get("ntuh_self_pay_price") if selected else None
        drug["ntuh_price_unit"] = self.infer_display_unit(drug)
        drug["ntuh_open_data"] = {
            "source_name": "NTUH QueryDrugInfoPhr",
            "source_url": BASE_URL,
            "query_date": query_date,
            "matched_rows_count": len(unique_candidates),
            "selected_confidence": confidence if selected else "no-match",
            "selected_code": selected.get("code") if selected else None,
            "selected_generic_name": selected.get("generic") if selected else None,
            "selected_chinese_name": selected.get("chinese") if selected else None,
            "selected_product_name": selected.get("product") if selected else None,
            "selected_nhi_price_text": selected.get("ntuh_nhi_price_text") if selected else None,
            "selected_self_pay_price_text": selected.get("ntuh_self_pay_price_text") if selected else None,
            "search_terms": self.make_search_terms(drug),
            "last_synced_at": last_synced_at,
        }

    def update_records(
        self,
        records: list[dict[str, Any]],
        selected_drugs: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        selected_names = {normalize_text(name) for name in (selected_drugs or [])}
        updated = 0
        for drug in records:
            if not self.should_update(drug, selected_names):
                continue
            self.update_drug(drug)
            updated += 1
        return {
            "updated_drugs": updated,
            "source_url": BASE_URL,
            "query_date": datetime.now().strftime("%Y-%m-%d"),
        }

    def update_file(
        self,
        data_path: str | Path,
        output_path: str | Path | None = None,
        selected_drugs: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        records = load_json_records(data_path)
        result = self.update_records(records, selected_drugs=selected_drugs)
        final_output = Path(output_path) if output_path else Path(data_path)
        save_json_records(final_output, records)
        result["output"] = str(final_output.resolve())
        return result
