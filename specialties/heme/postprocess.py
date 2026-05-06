from __future__ import annotations

import re

from specialties.heme.review_support import apply_heme_review_support


def _apply_nhi_price_fallback(d: dict) -> None:
    """When the NHI open-data API returns 0.00, fall back to the NTUH-page NHI price text."""
    if (d.get("nhi_price") or 0) != 0:
        return
    text = (d.get("ntuh_open_data") or {}).get("selected_nhi_price_text", "") or ""
    m = re.match(r"(\d+)", text.strip())
    if not m:
        return
    price = float(m.group(1))
    if price <= 0:
        return
    d["nhi_price"] = price
    d["nhi_price_source"] = "ntuh_fallback"
    for f in d.get("formulations", []):
        if f.get("is_primary") and (f.get("nhi_price") or 0) == 0:
            f["nhi_price"] = price


def apply_heme_rules(drugs: list[dict]) -> list[dict]:
    for d in drugs:
        tags = d.setdefault("clinical_tags", {})
        d.pop("review_support", None)

        if d["id"] == 1525:
            tags.pop("cd20", None)
            tags["btk"] = True

        if d["id"] == 1542:
            tags.pop("cd20", None)
            tags["btk"] = True

        if d["id"] == 1564:
            tags.pop("cd20", None)
            tags["btk"] = True

        if d["id"] == 1561:
            tags.pop("cd20", None)
            tags["bcl2"] = True
            d["trade_names"] = "Venclexta"

        if d["id"] == 1533:
            d["trade_names"] = "Ara-C"
            tags["disease"] = ["AML", "MDS", "ALL"]
            tags["phase"] = ["initial", "relapsed"]
            d.setdefault("manual_review", {})
            d["manual_review"]["verification_priority"] = "high"

        if d["id"] == 1532:
            tags["disease"] = ["CLL", "lymphoma", "myeloma"]
            tags["phase"] = ["initial", "relapsed"]

        if d["id"] == 1536:
            tags["disease"] = ["myeloma", "lymphoma"]
            tags["phase"] = ["initial", "relapsed"]

        if d["id"] == 1537:
            tags["disease"] = ["lymphoma", "myeloma"]

        if d["id"] == 1550:
            tags["disease"] = ["lymphoma"]

        if d["id"] == 1563:
            tags["disease"] = ["lymphoma"]
            tags["phase"] = ["initial", "relapsed"]

        if d["id"] == 1555:
            tags["disease"] = ["CLL", "lymphoma"]

        if d["id"] == 1526:
            d["trade_names"] = "Vidaza / Winduza"

        if d["id"] == 1548:
            d["trade_names"] = "Tasigna"

        if d["id"] == 1530:
            d["therapy_line"] = 1
            d["therapy_line_source"] = "健保規定"

        if d["id"] == 1531:
            d["therapy_line"] = 2
            d["therapy_line_source"] = "健保規定"

        if d["id"] == 1538:
            d["therapy_line"] = 3
            d["therapy_line_source"] = "健保規定"

        if d["id"] == 1551:
            d["therapy_line"] = 3
            d["therapy_line_source"] = "健保規定"

        if d["id"] == 1532:
            d["therapy_line_source"] = "NCCN"

        if d["id"] == 1536:
            d["therapy_line_source"] = "NCCN"

        if d["id"] == 1537:
            d["therapy_line_source"] = "NCCN"

        if d["id"] == 1550:
            d["therapy_line_source"] = "NCCN"

        if d["id"] == 1563:
            d["therapy_line_source"] = "NCCN"

        if d["id"] == 1555:
            d["therapy_line_source"] = "待確認"

        if d["id"] == 1558:
            d["therapy_line_source"] = "待確認"

        if d["id"] == 1536:
            d["data_note"] = (
                "⚠ 資料缺漏說明：本筆健保給付規定文字為 Ozurdex（玻璃體內植入劑，眼科適應症），"
                "非口服 Dexamethasone 4mg 錠用於血液腫瘤化療方案之規定。"
                "血液腫瘤科使用口服 Dexamethasone（如 VD、Rd、VRd 方案）依化療方案申請，"
                "藥品健保單價為口服錠劑價格。"
            )

        if d["id"] == 1537:
            d["data_note"] = (
                "⚠ 資料缺漏說明：本筆健保給付規定文字為 Lipo-Dox（脂質體多柔比星，用於卵巢癌、KS、乳癌），"
                "非傳統 Adriamycin（多柔比星注射劑）用於 CHOP/EPOCH 淋巴瘤方案之規定。"
                "血液腫瘤科使用 Doxorubicin 注射劑依化療方案申請，需補充正確藥品資料。"
            )

        if d["id"] == 1550:
            d["data_note"] = (
                "⚠ 資料缺漏說明：本筆健保給付規定文字為大腸直腸癌/胃癌/胰臟癌適應症，"
                "非 DHAP/R-DHAP 淋巴瘤拯救性化療方案之規定。"
                "血液腫瘤科使用 Oxaliplatin 依 DHAP 方案申請，需補充正確血液腫瘤科適應症資料。"
            )

        if d["id"] == 1533:
            d["data_note"] = (
                "⚠ 資料確認說明：依 2026/04/30 下載之健保開放資料，Cytarabine 100mg/vial"
                "（藥品代碼 BC25603221，生效日 110/07/01）之支付價為 0.00。"
                "系統保留官方回傳值，但此處不應直接解讀為「免費」或「無健保價」，建議人工複核主劑型與支付價。"
            )

        if d["id"] == 1555:
            d["data_note"] = (
                "⚠ 資料缺漏說明：本筆健保給付規定文字為類風濕性關節炎與天疱瘡（皮膚科/風濕科），"
                "非 CD20 陽性淋巴瘤（NHL/HL）或 CLL 之血液腫瘤科給付規定。"
                "Rituximab 用於淋巴瘤（R-CHOP、R-CVP 等方案）及 CLL 另有獨立健保給付規定，需補充正確血液腫瘤科適應症文字。"
            )

        if d["id"] == 1558:
            d["data_note"] = (
                "⚠ 資料缺漏說明：本筆健保給付規定文字為痲瘋性結節性紅斑（ENL）、陣發性夜間血紅素尿症（PNH）及非典型溶血尿毒症，"
                "非多發性骨髓瘤之給付規定。"
                "Thalidomide 用於多發性骨髓瘤目前需依個案申請，需補充正確骨髓瘤適應症資料。"
            )

        if "therapy_line_source" not in d:
            d["therapy_line_source"] = "健保規定"

        _apply_nhi_price_fallback(d)
        apply_heme_review_support(d)

    return drugs
