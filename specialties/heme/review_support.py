from __future__ import annotations


def select_field(key, label, options, placeholder="請選擇"):
    return {
        "key": key,
        "label": label,
        "type": "select",
        "placeholder": placeholder,
        "options": [{"value": str(v), "label": str(v)} for v in options],
    }


def number_field(key, label, placeholder="", step="1"):
    return {
        "key": key,
        "label": label,
        "type": "number",
        "placeholder": placeholder,
        "step": str(step),
    }


def text_field(key, label, placeholder=""):
    return {
        "key": key,
        "label": label,
        "type": "text",
        "placeholder": placeholder,
    }


def textarea_field(key, label, placeholder=""):
    return {
        "key": key,
        "label": label,
        "type": "textarea",
        "placeholder": placeholder,
    }


def cll_fields():
    return [
        select_field("ecog", "ECOG", ["0", "1", "2", "3", "4"]),
        select_field("del17p", "17p 缺失", ["是", "否", "未知"]),
        select_field("ighv", "IGHV 狀態", ["未突變", "已突變", "未知"]),
        number_field("prior_lines", "既往治療線數", "例如 2"),
        textarea_field("prior_regimens", "既往治療摘要", "請寫明 alkylating agent 與 anti-CD20 使用情形"),
        number_field("hb", "Hb (g/dL)", "例如 9.2", "0.1"),
        number_field("plt", "PLT (K/uL)", "例如 88", "1"),
        number_field("largest_node_cm", "最大淋巴結徑 (cm)", "例如 11", "0.1"),
        number_field("spleen_cm", "脾臟超出左肋下 (cm)", "例如 7", "0.1"),
        select_field("lymphocyte_rise", "2個月內淋巴球增加 ≥50%", ["是", "否", "未知"]),
        number_field("doubling_time_months", "淋巴球倍增時間(月)", "例如 4", "0.1"),
        select_field("autoimmune_refractory", "自體免疫併發症且類固醇無效", ["是", "否", "未知"]),
        select_field("symptomatic_extranodal", "症狀性淋巴結外病灶", ["是", "否", "未知"]),
        textarea_field("response_or_progression", "目前疾病狀態 / 送審摘要", "可填 relapse、progression、iwCLL 評估重點"),
    ]


def mcl_fields():
    return [
        text_field("diagnosis_date", "診斷日期", "例如 2025-11-03"),
        number_field("prior_regimen_count", "既往治療方案數", "例如 1"),
        textarea_field("prior_regimens", "既往治療摘要", "請列化療或標靶治療名稱與反應"),
        textarea_field("progression_evidence", "復發 / 無效證據", "請寫影像或病理進展重點"),
        text_field("latest_imaging_date", "最新影像日期", "例如 2026-04-12"),
        textarea_field("reapply_note", "續審評估摘要", "若為續用，請補前次治療反應與目前疾病狀態"),
    ]


def aml_unfit_fields():
    return [
        number_field("age", "年齡", "例如 76"),
        select_field("ecog", "ECOG", ["0", "1", "2", "3", "4"]),
        number_field("lvef", "LVEF (%)", "例如 45", "1"),
        number_field("dlco", "DLCO (%)", "例如 58", "1"),
        number_field("bilirubin_uln_multiple", "Bilirubin / ULN 倍數", "例如 1.8", "0.1"),
        select_field("prior_hma", "是否曾因 MDS 使用 azacitidine/decitabine", ["否", "是", "未知"]),
        textarea_field("diagnosis_summary", "AML 診斷摘要", "請填診斷日期、骨髓/流式/染色體重點"),
        textarea_field("organ_function_summary", "不適合高強度化療依據", "請填年齡、ECOG、LVEF、DLCO 或肝功能異常"),
        textarea_field("response_summary", "療效 / 續審摘要", "續用時請填第幾療程、療效與是否進展"),
    ]


def mds_fields():
    return [
        select_field("mds_subtype", "MDS 類型", ["RAEB", "RAEB-T", "CMML", "其他"]),
        number_field("marrow_blast_percent", "骨髓芽細胞 (%)", "例如 12", "0.1"),
        text_field("marrow_date", "骨髓檢查日期", "例如 2026-03-28"),
        text_field("cbc_date", "CBC/DC 日期", "例如 2026-04-25"),
        select_field("prior_hma", "曾使用 decitabine / azacitidine", ["未使用", "使用 decitabine", "使用 azacitidine", "未知"]),
        textarea_field("pathology_summary", "病理 / 血液摘要", "請填病理診斷、CBC/DC 與臨床狀態"),
        textarea_field("cycle_response", "治療反應摘要", "請填第幾療程、每4個月評估與是否惡化"),
    ]


def aml_maintenance_fields():
    return [
        number_field("age", "年齡", "例如 63"),
        select_field("cytogenetic_risk", "染色體風險", ["intermediate", "poor", "其他/未知"]),
        text_field("first_cr_date", "首次 CR / CRi 日期", "例如 2026-02-15"),
        textarea_field("induction_summary", "誘導 / 鞏固治療摘要", "請填 induction 與 consolidation 情形"),
        select_field("prior_hma", "先前是否使用 azacitidine / decitabine", ["否", "是", "未知"]),
        select_field("hsct_candidate", "是否適合 HSCT", ["不適合", "適合", "未評估"]),
        number_field("current_blast_percent", "目前周邊血 / 骨髓 blasts (%)", "例如 2", "0.1"),
        select_field("extramedullary_disease", "是否有新髓外侵犯", ["否", "是", "未知"]),
        textarea_field("maintenance_note", "維持治療摘要", "請填維持治療送審重點與追蹤計畫"),
    ]


def wm_fields():
    return [
        number_field("age", "年齡", "例如 71"),
        number_field("hb", "Hb (g/dL)", "例如 10.2", "0.1"),
        number_field("plt", "PLT (x10^9/L)", "例如 92", "1"),
        number_field("beta2_microglobulin", "β2-microglobulin (mg/L)", "例如 3.8", "0.1"),
        number_field("igm", "IgM (g/dL)", "例如 7.6", "0.1"),
        textarea_field("prior_regimens", "既往治療摘要", "需寫明單株抗體與靜脈 alkylating agent"),
        number_field("regimen_courses", "既往 chemoimmunotherapy 療程數", "例如 4"),
        textarea_field("relapse_summary", "復發 / 無效證據", "請填症狀、檢驗或影像進展重點"),
    ]


def fl_fields():
    return [
        number_field("prior_lines", "既往全身治療線數", "例如 2"),
        textarea_field("prior_regimens", "既往治療摘要", "需寫明 anti-CD20 與靜脈注射 alkylating agent"),
        select_field("who_grade", "WHO 分類 grade", ["I", "II", "IIIa", "其他/未知"]),
        number_field("largest_mass_cm", "最大單一腫瘤徑 (cm)", "例如 7.2", "0.1"),
        select_field("three_nodes_gt_3cm", "是否有 3 顆以上 >3cm 腫瘤", ["是", "否", "未知"]),
        number_field("spleen_length_cm", "脾臟長度 (cm)", "例如 17", "0.1"),
        select_field("vital_organ_compression", "是否造成 vital organ 壓迫", ["是", "否", "未知"]),
        select_field("lymphocytosis", "周邊血淋巴球 >5000/mm3", ["是", "否", "未知"]),
        select_field("cytopenia", "是否有血球低下", ["是", "否", "未知"]),
        select_field("b_symptoms", "是否有 B symptoms", ["是", "否", "未知"]),
        textarea_field("imaging_summary", "影像 / 疾病負荷摘要", "請填 bulky disease 或其他符合條件證據"),
    ]


def apply_heme_review_support(drug: dict) -> None:
    if drug["id"] == 1525:
        drug["review_support"] = {
            "intro": "血液科健保審查常需要把檢驗、既往治療與疾病進展重點先整理成可貼上的摘要。",
            "profiles": [
                {
                    "id": "acalabrutinib_mcl",
                    "label": "被套細胞淋巴瘤 MCL",
                    "subtitle": "至少接受過一種化學或標靶治療後復發 / 無效",
                    "docs": ["病理確診資料", "既往治療紀錄", "最新影像報告", "前次療效評估"],
                    "note": "首次申請以 4 個月為限；續審需補前次治療結果評估資料。",
                    "fields": mcl_fields(),
                },
                {
                    "id": "acalabrutinib_cll",
                    "label": "慢性淋巴球性白血病 CLL",
                    "subtitle": "ECOG、17p / IGHV、既往治療與疾病進展條件整理",
                    "docs": ["CLL 確診資料", "17p / IGHV 檢驗報告", "既往治療紀錄", "CBC / 影像評估"],
                    "note": "續審每 3 個月一次，需補 iwCLL 反應評估。",
                    "fields": cll_fields(),
                },
            ],
        }
    elif drug["id"] == 1526:
        drug["review_support"] = {
            "intro": "Azacitidine 的送審條件會依 MDS、AML 合併 venetoclax、AML 維持治療而不同。",
            "profiles": [
                {
                    "id": "azacitidine_mds",
                    "label": "高風險 MDS / CMML",
                    "subtitle": "RAEB / RAEB-T / CMML 送審摘要",
                    "docs": ["骨髓病理報告", "每 4 個月骨髓檢查", "CBC/DC", "臨床療效評估摘要"],
                    "note": "續用免再事審，但病歷仍需完整保留骨髓與療效評估資料。",
                    "fields": mds_fields(),
                },
                {
                    "id": "azacitidine_aml_combo",
                    "label": "AML 合併 Venetoclax",
                    "subtitle": "初診 AML 且不適合高強度化療",
                    "docs": ["AML 診斷資料", "ECOG / 年齡 / 心肺肝功能證據", "既往 MDS 用藥史", "療效評估"],
                    "note": "每 2 個療程需續審；最多給付 6 個療程。",
                    "fields": aml_unfit_fields(),
                },
                {
                    "id": "azacitidine_maintenance",
                    "label": "AML 維持治療 Onureg",
                    "subtitle": "55 歲以上、中度或高度不良風險染色體、首次 CR/CRi",
                    "docs": ["染色體報告", "CR / CRi 證明", "誘導 / 鞏固治療摘要", "追蹤骨髓 / 周邊血資料"],
                    "note": "初次申請 3 個療程；每 3 個療程續審，可治療至復發或無法耐受為止。",
                    "fields": aml_maintenance_fields(),
                },
            ],
        }
    elif drug["id"] == 1561:
        drug["review_support"] = {
            "intro": "Venetoclax 在 CLL 與 AML 的給付前提差異很大，建議分開整理。",
            "profiles": [
                {
                    "id": "venetoclax_cll",
                    "label": "CLL 17p 缺失",
                    "subtitle": "17p 缺失、既往治療與疾病進展條件",
                    "docs": ["17p 缺失檢驗報告", "既往含 anti-CD20 / alkylating agent 治療紀錄", "CBC / 影像 / iwCLL 評估"],
                    "note": "每 3 個月需續審；需達 partial remission 或 complete remission 才續給付。",
                    "fields": cll_fields(),
                },
                {
                    "id": "venetoclax_aml",
                    "label": "AML 不適合高強度化療",
                    "subtitle": "合併 azacitidine 或低劑量 cytarabine",
                    "docs": ["AML 診斷資料", "高齡或器官功能不適合高強度化療證據", "既往 MDS 用藥史", "療效評估"],
                    "note": "若合併 azacitidine 最多 6 個療程；若合併低劑量 cytarabine 最多 4 個療程。",
                    "fields": aml_unfit_fields(),
                },
            ],
        }
    elif drug["id"] == 1564:
        drug["review_support"] = {
            "intro": "Zanubrutinib 目前在本系統先整理 CLL、華氏巨球蛋白血症與濾泡性淋巴瘤三種常見送審情境。",
            "profiles": [
                {
                    "id": "zanubrutinib_cll",
                    "label": "CLL",
                    "subtitle": "ECOG、17p / IGHV、既往治療與疾病進展條件",
                    "docs": ["CLL 確診資料", "17p / IGHV 檢驗報告", "既往治療紀錄", "CBC / 影像 / iwCLL 評估"],
                    "note": "每 3 個月續審一次；具有 17p 缺失病人與 acalabrutinib / ibrutinib / venetoclax 合併計算總療程。",
                    "fields": cll_fields(),
                },
                {
                    "id": "zanubrutinib_wm",
                    "label": "華氏巨球蛋白血症 WM",
                    "subtitle": "需至少符合 5 項風險條件中的 3 項，且先前治療至少 4 個療程",
                    "docs": ["WM 確診資料", "Hb / PLT / β2-microglobulin / IgM 檢驗", "既往 chemoimmunotherapy 紀錄", "療效評估"],
                    "note": "首次申請 4 個月；之後每 3 個月續審。",
                    "fields": wm_fields(),
                },
                {
                    "id": "zanubrutinib_fl",
                    "label": "濾泡性淋巴瘤 FL",
                    "subtitle": "至少兩線全身治療後復發 / 無效，並符合疾病負荷條件",
                    "docs": ["病理 grade 報告", "既往 anti-CD20 與 alkylating agent 紀錄", "最新影像報告", "CBC / 症狀紀錄"],
                    "note": "每 3 個月續審；需補 PR / CR 反應評估。",
                    "fields": fl_fields(),
                },
            ],
        }
