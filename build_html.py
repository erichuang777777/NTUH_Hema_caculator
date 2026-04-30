"""
NHI_Heme_Calculator HTML builder
從 heme_drugs_clean.json (原始 NHI 資料) 重建 index.html

資料來源標記規則：
- nhi_price: 全民健康保險藥物給付項目及支付標準藥價（健保藥價基準 115/04/01）
- indication / conditions: 全民健康保險藥物給付項目及支付標準
- therapy_line_source: 健保規定 = NHI 文件明確標示 / NCCN = 指引推算 / 待確認 = 無文件依據
- 台大藥價: 目前無血液腫瘤藥品台大藥局資料，不顯示
"""
import json

# 讀取原始 NHI 資料（未經覆蓋的原版本）
with open('D:/新增資料夾/Git_NHI_Drug_Caculator/NHI_Heme_Calculator/data/heme_drugs_clean.json','r',encoding='utf-8') as f:
    drugs = json.load(f)

# ── 資料校正（所有修改皆有文件依據） ─────────────────────────────────────────

for d in drugs:
    gn = d['generic_name']
    tags = d.setdefault('clinical_tags', {})

    # ── 修正 clinical_tags ──

    # Acalabrutinib: 移除誤標的 cd20，加上 btk
    if d['id'] == 1525:
        tags.pop('cd20', None)
        tags['btk'] = True

    # Ibrutinib: 移除誤標的 cd20，加上 btk
    if d['id'] == 1542:
        tags.pop('cd20', None)
        tags['btk'] = True

    # Zanubrutinib: 移除誤標的 cd20，加上 btk
    if d['id'] == 1564:
        tags.pop('cd20', None)
        tags['btk'] = True

    # Venetoclax: 移除誤標的 cd20（venetoclax 是 BCL-2 抑制劑，非 anti-CD20）
    if d['id'] == 1561:
        tags.pop('cd20', None)
        tags['bcl2'] = True
        d['trade_names'] = 'Venclexta'

    # Cytarabine: 原始 trade_names 為 'AML'（資料錯誤），修正為 Ara-C
    if d['id'] == 1533:
        d['trade_names'] = 'Ara-C'
        tags['disease'] = ['AML', 'MDS', 'ALL']
        tags['phase'] = ['initial', 'relapsed']

    # Cyclophosphamide: 補充疾病標籤（依 NCCN，為骨幹化療藥物）
    if d['id'] == 1532:
        tags['disease'] = ['CLL', 'lymphoma', 'myeloma']
        tags['phase'] = ['initial', 'relapsed']

    # Dexamethasone: 補充疾病標籤
    if d['id'] == 1536:
        tags['disease'] = ['myeloma', 'lymphoma']
        tags['phase'] = ['initial', 'relapsed']

    # Doxorubicin: 補充疾病標籤
    if d['id'] == 1537:
        tags['disease'] = ['lymphoma', 'myeloma']

    # Oxaliplatin: 補充疾病標籤
    if d['id'] == 1550:
        tags['disease'] = ['lymphoma']

    # Vinblastine: 補充疾病標籤
    if d['id'] == 1563:
        tags['disease'] = ['lymphoma']
        tags['phase'] = ['initial', 'relapsed']

    # Rituximab: 補充疾病標籤
    if d['id'] == 1555:
        tags['disease'] = ['CLL', 'lymphoma']

    # Azacitidine: 更新 trade_names（包含 Winduza 新劑型）
    if d['id'] == 1526:
        d['trade_names'] = 'Vidaza / Winduza'

    # Nilotinib: 補充 trade_names
    if d['id'] == 1548:
        d['trade_names'] = 'Tasigna'

    # ── 治療線校正（依 NHI 給付規定文字） ──
    # 所有校正皆有 indication/conditions 文字為依據，不憑空推測

    # Brentuximab vedotin (1530): 指示「先前未曾接受治療」之 HL/sALCL 一線使用
    # 文件依據：indication 「與ABVD併用適用於先前未曾接受治療」
    if d['id'] == 1530:
        d['therapy_line'] = 1
        d['therapy_line_source'] = '健保規定'

    # Carfilzomib (1531): 最早適應症需「先前曾接受至少一種含bortezomib或lenalidomide之療法治療失敗」
    # = 至少接受過 1 種含標靶療法 → 第 2 線 起
    # 文件依據：indication「與isatuximab/dexamethasone併用...先前曾接受至少一種含bortezomib或lenalidomide之療法治療失敗」
    if d['id'] == 1531:
        d['therapy_line'] = 2
        d['therapy_line_source'] = '健保規定'

    # Elotuzumab (1538): 「曾接受過至少兩種療法（包括lenalidomide和蛋白酶體抑制劑）」= 第 3 線
    # 文件依據：indication 第一句
    if d['id'] == 1538:
        d['therapy_line'] = 3
        d['therapy_line_source'] = '健保規定'

    # Pomalidomide (1551): 「先前接受過含lenalidomide和bortezomib在內的至少兩種療法」= 第 3 線
    # 文件依據：indication 第一句
    if d['id'] == 1551:
        d['therapy_line'] = 3
        d['therapy_line_source'] = '健保規定'

    # ── 治療線來源標記（骨幹化療藥物無獨立 NHI 血液科適應症文件） ──

    # Cyclophosphamide: 無獨立 NHI 血液腫瘤給付規定，依方案使用
    if d['id'] == 1532:
        d['therapy_line_source'] = 'NCCN'

    # Dexamethasone: 健保登載適應症為 Ozurdex（眼科），非口服 dex 血液科用途
    if d['id'] == 1536:
        d['therapy_line_source'] = 'NCCN'

    # Doxorubicin (Lipo-Dox): 健保登載適應症為脂質體劑型卵巢癌/KS/乳癌，非 CHOP 用途
    if d['id'] == 1537:
        d['therapy_line_source'] = 'NCCN'

    # Oxaliplatin: 健保登載適應症為大腸直腸癌/胃癌，非血液腫瘤
    if d['id'] == 1550:
        d['therapy_line_source'] = 'NCCN'

    # Vinblastine: 無獨立 NHI 血液腫瘤給付規定，依 ABVD 方案使用
    if d['id'] == 1563:
        d['therapy_line_source'] = 'NCCN'

    # Rituximab: 健保登載適應症為類風濕性關節炎/天疱瘡；淋巴瘤/CLL 血液腫瘤用途依另案申請
    # 治療線無法從現有文字確認
    if d['id'] == 1555:
        d['therapy_line_source'] = '待確認'

    # Thalidomide: 健保登載適應症為痲瘋病/PNH/aHUS；骨髓瘤用途需另案申請
    if d['id'] == 1558:
        d['therapy_line_source'] = '待確認'

    # ── 資料品質備注（data_note：說明資料缺漏或不一致，顯示於 UI 警告框） ──

    # Dexamethasone: 現有 NHI 資料為 Ozurdex 眼科劑型
    if d['id'] == 1536:
        d['data_note'] = (
            '⚠ 資料缺漏說明：本筆健保給付規定文字為 Ozurdex（玻璃體內植入劑，眼科適應症），'
            '非口服 Dexamethasone 4mg 錠用於血液腫瘤化療方案之規定。'
            '血液腫瘤科使用口服 Dexamethasone（如 VD、Rd、VRd 方案）依化療方案申請，'
            '藥品健保單價為口服錠劑價格。'
        )

    # Doxorubicin (Lipo-Dox): NHI 資料為脂質體劑型，非 CHOP 用 Adriamycin
    if d['id'] == 1537:
        d['data_note'] = (
            '⚠ 資料缺漏說明：本筆健保給付規定文字為 Lipo-Dox（脂質體多柔比星，用於卵巢癌、KS、乳癌），'
            '非傳統 Adriamycin（多柔比星注射劑）用於 CHOP/EPOCH 淋巴瘤方案之規定。'
            '血液腫瘤科使用 Doxorubicin 注射劑依化療方案申請，需補充正確藥品資料。'
        )

    # Oxaliplatin: NHI 資料為消化系癌症適應症
    if d['id'] == 1550:
        d['data_note'] = (
            '⚠ 資料缺漏說明：本筆健保給付規定文字為大腸直腸癌/胃癌/胰臟癌適應症，'
            '非 DHAP/R-DHAP 淋巴瘤拯救性化療方案之規定。'
            '血液腫瘤科使用 Oxaliplatin 依 DHAP 方案申請，需補充正確血液腫瘤科適應症資料。'
        )

    # Rituximab: NHI 資料為類風濕性關節炎/天疱瘡
    if d['id'] == 1555:
        d['data_note'] = (
            '⚠ 資料缺漏說明：本筆健保給付規定文字為類風濕性關節炎與天疱瘡（皮膚科/風濕科），'
            '非 CD20 陽性淋巴瘤（NHL/HL）或 CLL 之血液腫瘤科給付規定。'
            'Rituximab 用於淋巴瘤（R-CHOP、R-CVP 等方案）及 CLL 另有獨立健保給付規定，需補充正確血液腫瘤科適應症文字。'
        )

    # Thalidomide: NHI 資料為痲瘋病/PNH/aHUS
    if d['id'] == 1558:
        d['data_note'] = (
            '⚠ 資料缺漏說明：本筆健保給付規定文字為痲瘋性結節性紅斑（ENL）、陣發性夜間血紅素尿症（PNH）及非典型溶血尿毒症，'
            '非多發性骨髓瘤之給付規定。'
            'Thalidomide 用於多發性骨髓瘤目前需依個案申請，需補充正確骨髓瘤適應症資料。'
        )

    # 所有藥品確認 therapy_line_source 已設定
    if 'therapy_line_source' not in d:
        d['therapy_line_source'] = '健保規定'

# 輸出供 JS 嵌入的 JSON
inline_json = json.dumps(drugs, ensure_ascii=False, separators=(',', ':'))

# 儲存供後續參考
with open('D:/新增資料夾/Git_NHI_Drug_Caculator/NHI_Heme_Calculator/data/heme_final.json','w',encoding='utf-8') as f:
    json.dump(drugs, f, ensure_ascii=False, indent=2)

# ── CSS ──────────────────────────────────────────────────────────────────────

CSS = """
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#F8F9FA;--surface:#FFFFFF;--surface-2:#F1F5F9;--border:#E2E8F0;--border-2:#CBD5E1;
  --text:#0F172A;--text-2:#334155;--text-muted:#64748B;
  --heme:#1E3A8A;--heme-bg:#EFF6FF;--heme-border:#BFDBFE;--heme-light:#3B82F6;
  --nhi:#047857;--nhi-bg:#ECFDF5;--nhi-border:#6EE7B7;
  --auth:#B45309;--auth-bg:#FFFBEB;--auth-border:#FDE68A;
  --warn:#92400E;--warn-bg:#FEF3C7;--warn-border:#FDE68A;
  --primary:#1D4ED8;--primary-hover:#1E40AF;
  --r-sm:6px;--r-md:10px;--r-lg:14px;--r-xl:18px;
}
body{font-family:'Noto Sans TC',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);line-height:1.6;font-size:15px}
.header{background:#0F172A;color:#fff;padding:.9rem 1.5rem;display:flex;align-items:center;gap:1rem;position:sticky;top:0;z-index:100}
.header-title{font-size:1.05rem;font-weight:700}
.header-sub{font-size:.75rem;color:#94A3B8;margin-left:.2rem}
.header-badge{margin-left:auto;background:#1E40AF;color:#BFDBFE;font-size:.72rem;font-weight:600;padding:.25rem .7rem;border-radius:20px;cursor:pointer;border:1px solid #3B82F6;white-space:nowrap}
.header-badge:hover{background:#1D4ED8}
.layout{display:flex;min-height:calc(100vh - 56px)}
.sidebar{width:220px;flex-shrink:0;background:var(--surface);border-right:1px solid var(--border);padding:1rem .75rem;position:sticky;top:56px;height:calc(100vh - 56px);overflow-y:auto}
.main{flex:1;padding:1.25rem;min-width:0}
.sidebar-section{margin-bottom:1.25rem}
.sidebar-label{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--text-muted);margin-bottom:.5rem;padding:0 .25rem}
.filter-btn{display:block;width:100%;text-align:left;padding:.4rem .65rem;border-radius:var(--r-sm);border:none;background:none;cursor:pointer;font-size:.78rem;color:var(--text-2);font-family:inherit;transition:all .15s;line-height:1.4}
.filter-btn:hover{background:var(--surface-2)}
.filter-btn.active{background:var(--heme-bg);color:var(--heme);font-weight:600}
.filter-btn .count{float:right;font-size:.68rem;background:var(--surface-2);color:var(--text-muted);border-radius:10px;padding:1px 6px}
.filter-btn.active .count{background:rgba(30,58,138,.12);color:var(--heme)}
.mol-filter{display:flex;flex-wrap:wrap;gap:.3rem}
.mol-btn{padding:.22rem .5rem;border-radius:20px;border:1px solid var(--border-2);background:var(--surface);font-size:.7rem;cursor:pointer;font-family:inherit;color:var(--text-muted);transition:all .15s}
.mol-btn:hover{border-color:var(--heme-light);color:var(--heme)}
.mol-btn.active{background:var(--heme-bg);border-color:var(--heme);color:var(--heme);font-weight:600}
.search-wrap{display:flex;gap:.5rem;margin-bottom:1rem;align-items:center}
.search-input{flex:1;padding:.5rem .85rem;border:1.5px solid var(--border);border-radius:var(--r-md);font-size:.88rem;font-family:inherit;background:var(--surface);color:var(--text)}
.search-input:focus{outline:none;border-color:var(--heme-light)}
.result-count{font-size:.78rem;color:var(--text-muted);white-space:nowrap}
.cards-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1rem}
.drug-flip-wrap{perspective:1200px;cursor:pointer}
.drug-flip-inner{position:relative;width:100%;min-height:130px;transition:transform .45s cubic-bezier(.4,0,.2,1);transform-style:preserve-3d}
.drug-flip-wrap.flipped .drug-flip-inner{transform:rotateY(180deg)}
.drug-flip-front,.drug-flip-back{backface-visibility:hidden;-webkit-backface-visibility:hidden}
.drug-flip-front{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-lg);padding:1rem;position:absolute;top:0;left:0;width:100%;min-height:130px}
.drug-flip-back{position:absolute;top:0;left:0;width:100%;min-height:130px;background:var(--heme-bg);border:1px solid var(--heme-border);border-radius:var(--r-lg);padding:1rem;transform:rotateY(180deg);display:flex;flex-direction:column;justify-content:space-between}
.drug-card-header{display:flex;align-items:flex-start;gap:.6rem;margin-bottom:.5rem}
.drug-icon{width:36px;height:36px;border-radius:var(--r-md);background:var(--heme-bg);color:var(--heme);display:flex;align-items:center;justify-content:center;font-size:.85rem;flex-shrink:0;font-weight:800;border:1px solid var(--heme-border)}
.drug-name{font-size:.9rem;font-weight:700;color:var(--text);line-height:1.3}
.drug-trade{font-size:.75rem;color:var(--text-muted);margin-top:.1rem}
.drug-tags{display:flex;flex-wrap:wrap;gap:.3rem;margin-top:.5rem}
.tag{display:inline-flex;align-items:center;font-size:.68rem;font-weight:600;padding:.18rem .5rem;border-radius:20px}
.tag-disease{background:#EFF6FF;color:#1D4ED8}
.tag-nhi{background:var(--nhi-bg);color:var(--nhi)}
.tag-auth{background:var(--auth-bg);color:var(--auth)}
.tag-mol{background:#F3E8FF;color:#7C3AED}
.tag-line{background:#F8FAFC;color:var(--text-muted);border:1px solid var(--border)}
.tag-warn{background:var(--warn-bg);color:var(--warn)}
.tag-tbd{background:#F1F5F9;color:#64748B;border:1px dashed #94A3B8}
.drug-price{font-size:.76rem;color:var(--text-muted);margin-top:.45rem;padding-top:.45rem;border-top:1px solid var(--border)}
.drug-price strong{color:var(--text-2);font-weight:600}
.back-info{font-size:.78rem;color:var(--text-2);line-height:1.8}
.back-info strong{color:var(--heme);margin-right:.3rem}
.back-btns{display:flex;gap:.5rem;margin-top:.5rem}
.back-btn{flex:1;padding:.38rem;border-radius:var(--r-sm);border:1px solid var(--heme-border);background:var(--surface);color:var(--heme);font-size:.75rem;font-weight:600;cursor:pointer;font-family:inherit;transition:all .15s}
.back-btn:hover{background:var(--heme);color:#fff}
.back-btn.primary{background:var(--heme);color:#fff}
.back-btn.primary:hover{background:var(--primary-hover)}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:200;align-items:center;justify-content:center;padding:1rem}
.modal-overlay.open{display:flex}
.modal{background:var(--surface);border-radius:var(--r-xl);max-width:680px;width:100%;max-height:90vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,.25)}
.modal-header{padding:1.25rem 1.5rem 1rem;border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--surface);z-index:1;display:flex;align-items:flex-start;gap:.75rem}
.modal-icon{width:44px;height:44px;border-radius:var(--r-lg);background:var(--heme-bg);color:var(--heme);display:flex;align-items:center;justify-content:center;font-size:1rem;font-weight:800;flex-shrink:0;border:1px solid var(--heme-border)}
.modal-title{font-size:1.05rem;font-weight:800;color:var(--text)}
.modal-subtitle{font-size:.75rem;color:var(--text-muted);margin-top:.15rem}
.modal-close{margin-left:auto;width:32px;height:32px;border-radius:50%;border:none;background:var(--surface-2);cursor:pointer;font-size:1rem;color:var(--text-muted);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.modal-close:hover{background:var(--border)}
.modal-body{padding:1.25rem 1.5rem}
/* Source label inline */
.src-tag{font-size:.65rem;font-weight:600;padding:.12rem .45rem;border-radius:10px;vertical-align:middle;margin-left:.35rem}
.src-nhi{background:var(--nhi-bg);color:var(--nhi);border:1px solid var(--nhi-border)}
.src-nccn{background:#F0F9FF;color:#0369A1;border:1px solid #BAE6FD}
.src-tbd{background:#F1F5F9;color:#64748B;border:1px dashed #CBD5E1}
/* Section header with source badge */
.section-hd{display:flex;align-items:center;gap:.5rem;margin-bottom:.5rem}
.section-hd-label{font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:var(--text-muted)}
.section-hd .src-tag{font-size:.63rem}
/* Data warning box */
.data-warn{background:var(--warn-bg);border:1px solid var(--warn-border);border-radius:var(--r-md);padding:.7rem .9rem;margin-bottom:1rem;font-size:.78rem;color:var(--warn);line-height:1.6}
.data-warn strong{display:block;margin-bottom:.2rem;font-size:.8rem}
/* Detail rows */
.detail-divider{border:none;border-top:1px solid var(--border);margin:.9rem 0}
.detail-row{display:flex;gap:.5rem;margin-bottom:.35rem;align-items:flex-start}
.detail-row dt{font-size:.76rem;color:var(--text-muted);min-width:75px;flex-shrink:0;padding-top:.1rem}
.detail-row dd{font-size:.8rem;color:var(--text-2);font-weight:500}
.detail-section{margin-bottom:1.1rem}
.cond-list{list-style:none;padding:0}
.cond-list li{font-size:.8rem;color:var(--text-2);line-height:1.7;padding:.15rem 0 .15rem 1.1rem;position:relative}
.cond-list li::before{content:"\\25B8";position:absolute;left:0;color:var(--heme-light)}
/* Cost calc */
.calc-box{background:var(--heme-bg);border:1px solid var(--heme-border);border-radius:var(--r-lg);padding:1rem;margin-top:.75rem}
.calc-title{font-size:.8rem;font-weight:700;color:var(--heme);margin-bottom:.7rem}
.calc-row{display:flex;align-items:center;gap:.5rem;margin-bottom:.4rem;flex-wrap:wrap}
.calc-label{font-size:.76rem;color:var(--text-muted);min-width:90px}
.calc-input{width:75px;padding:.3rem .45rem;border:1px solid var(--heme-border);border-radius:var(--r-sm);font-size:.8rem;font-family:inherit;background:var(--surface)}
.calc-input:focus{outline:none;border-color:var(--heme)}
.calc-unit{font-size:.73rem;color:var(--text-muted)}
.calc-result{background:var(--heme);color:#fff;border-radius:var(--r-md);padding:.65rem 1rem;margin-top:.65rem;font-size:.84rem;font-weight:600;text-align:center}
.calc-result span{font-size:1.1rem;font-weight:800}
.calc-btn{padding:.35rem .75rem;background:var(--heme);color:#fff;border:none;border-radius:var(--r-sm);font-size:.78rem;font-weight:600;cursor:pointer;font-family:inherit}
.calc-btn:hover{background:var(--primary-hover)}
/* Changelog */
.cl-version{margin-bottom:1.25rem}
.cl-ver-badge{display:inline-block;background:var(--heme-bg);color:var(--heme);font-size:.73rem;font-weight:700;padding:.2rem .65rem;border-radius:20px;margin-bottom:.5rem;border:1px solid var(--heme-border)}
.cl-items{list-style:none;padding:0}
.cl-items li{font-size:.8rem;color:var(--text-2);padding:.12rem 0 .12rem 1.1rem;position:relative}
.cl-items li::before{content:"\\2736";position:absolute;left:0;color:var(--heme-light);font-size:.6rem;top:.3rem}
.empty-state{text-align:center;padding:3rem 1rem;color:var(--text-muted);grid-column:1/-1}
.empty-icon{font-size:2.5rem;margin-bottom:.75rem}
.mobile-filter-bar{display:none;flex-wrap:wrap;gap:.35rem;padding:.65rem 1rem;background:var(--surface);border-bottom:1px solid var(--border)}
@media(max-width:640px){
  .sidebar{display:none}
  .main{padding:1rem}
  .cards-grid{grid-template-columns:1fr}
  .mobile-filter-bar{display:flex;overflow-x:auto;flex-wrap:nowrap}
}
"""

# ── JavaScript ────────────────────────────────────────────────────────────────

JS_TEMPLATE = r"""
const _HD = DRUGDATA;

const DISEASES=[
  {k:'all',l:'全部疾病'},
  {k:'CLL',l:'CLL 慢性淋巴性白血病'},
  {k:'lymphoma',l:'淋巴瘤 Lymphoma'},
  {k:'myeloma',l:'多發性骨髓瘤 MM'},
  {k:'CML',l:'CML 慢性骨髓性白血病'},
  {k:'AML',l:'AML 急性骨髓性白血病'},
  {k:'MDS',l:'MDS 骨髓發育不良'},
  {k:'ALL',l:'ALL 急性淋巴性白血病'},
];
const MOLS=[
  {k:'btk',l:'BTK抑制劑'},
  {k:'cd20',l:'Anti-CD20'},
  {k:'flt3',l:'FLT3'},
  {k:'ph_positive',l:'Ph+/BCR-ABL'},
  {k:'bcl2',l:'BCL-2'},
];
const DNM={CLL:'CLL',lymphoma:'淋巴瘤',myeloma:'骨髓瘤',CML:'CML',AML:'AML',MDS:'MDS',ALL:'ALL',GIST:'GIST'};
const dn=k=>DNM[k]||k;

let aDis='all',aMol=new Set(),aLine='all';

function cntDis(k){return k==='all'?_HD.length:_HD.filter(d=>(d.clinical_tags?.disease||[]).includes(k)).length;}

function renderSidebar(){
  document.getElementById('dFilt').innerHTML=DISEASES.map(d=>
    `<button class="filter-btn${aDis===d.k?' active':''}" onclick="setDis('${d.k}')">${d.l}<span class="count">${cntDis(d.k)}</span></button>`
  ).join('');
  document.getElementById('mFilt').innerHTML=MOLS.map(m=>
    `<button class="mol-btn${aMol.has(m.k)?' active':''}" onclick="toggleMol('${m.k}')">${m.l}</button>`
  ).join('');
  document.getElementById('lFilt').innerHTML=[['all','全部'],['1','第一線'],['2','第二線'],['3','第三線+']].map(([l,lb])=>
    `<button class="filter-btn${aLine===l?' active':''}" onclick="setLine('${l}')">${lb}</button>`
  ).join('');
  document.getElementById('mobFilt').innerHTML=DISEASES.map(d=>
    `<button class="mol-btn${aDis===d.k?' active':''}" onclick="setDis('${d.k}')" style="white-space:nowrap">${d.k==='all'?'全部':d.k}</button>`
  ).join('');
}
function setDis(k){aDis=k;renderSidebar();renderCards();}
function toggleMol(k){aMol.has(k)?aMol.delete(k):aMol.add(k);renderSidebar();renderCards();}
function setLine(l){aLine=l;renderSidebar();renderCards();}

function getFilt(){
  const q=(document.getElementById('sIn')?.value||'').trim().toLowerCase();
  return _HD.filter(d=>{
    const dis=d.clinical_tags?.disease||[];
    if(aDis!=='all'&&!dis.includes(aDis)) return false;
    if(aMol.size>0&&![...aMol].every(m=>d.clinical_tags?.[m])) return false;
    if(aLine==='1'&&(d.therapy_line||1)>1) return false;
    if(aLine==='2'&&d.therapy_line!==2) return false;
    if(aLine==='3'&&(d.therapy_line||1)<3) return false;
    if(q&&!(d.generic_name+' '+(d.trade_names||'')+' '+d.indication+' '+(dis.join(' '))).toLowerCase().includes(q)) return false;
    return true;
  });
}

function ini(n){
  const w=n.split(/[\s\-]+/);
  return w.length>=2?(w[0][0]+(w[1][0]||'')).toUpperCase():n.substring(0,2).toUpperCase();
}
function molT(d){
  const r=[];
  if(d.clinical_tags?.btk) r.push('<span class="tag tag-mol">BTK</span>');
  if(d.clinical_tags?.cd20) r.push('<span class="tag tag-mol">CD20</span>');
  if(d.clinical_tags?.flt3) r.push('<span class="tag tag-mol">FLT3</span>');
  if(d.clinical_tags?.ph_positive) r.push('<span class="tag tag-mol">Ph+</span>');
  if(d.clinical_tags?.bcl2) r.push('<span class="tag tag-mol">BCL-2</span>');
  return r.join('');
}

// 來源標籤
function lineSrcTag(src){
  if(src==='健保規定') return '<span class="src-tag src-nhi">健保規定</span>';
  if(src==='NCCN') return '<span class="src-tag src-nccn">NCCN</span>';
  return '<span class="src-tag src-tbd">待確認</span>';
}

function renderCards(){
  const drugs=getFilt();
  document.getElementById('rCnt').textContent=`共 ${drugs.length} 種`;
  const grid=document.getElementById('cGrid');
  if(!drugs.length){
    grid.innerHTML='<div class="empty-state"><div class="empty-icon">&#128269;</div><p>找不到符合條件的藥物</p></div>';
    return;
  }
  grid.innerHTML=drugs.map(d=>{
    const dis=d.clinical_tags?.disease||[];
    const diT=dis.map(x=>`<span class="tag tag-disease">${dn(x)}</span>`).join('');
    const mT=molT(d);
    const aT=d.prior_auth?'<span class="tag tag-auth">事前審查</span>':'';
    const lT=`<span class="tag tag-line">L${d.therapy_line||1}</span>`;
    const warnT=d.data_note?'<span class="tag tag-warn">&#9888; 資料待確認</span>':'';
    const pT=d.nhi_price?`健保藥價 <strong>NT$${d.nhi_price.toLocaleString()}</strong>/<small>${d.price_unit||'unit'}</small>`:'';
    return `<div class="drug-flip-wrap" id="fp-${d.id}" style="height:${130+(dis.length>2?16:0)+(d.data_note?0:0)}px">
      <div class="drug-flip-inner">
        <div class="drug-flip-front" onclick="flipC(${d.id})">
          <div class="drug-card-header">
            <div class="drug-icon">${ini(d.generic_name)}</div>
            <div><div class="drug-name">${d.generic_name}</div><div class="drug-trade">${d.trade_names||'(通用名)'}</div></div>
          </div>
          <div class="drug-tags">${diT}${mT}${aT}${lT}${warnT}</div>
          ${pT?`<div class="drug-price">${pT}</div>`:''}
        </div>
        <div class="drug-flip-back">
          <div class="back-info">
            <div><strong>藥品：</strong>${d.generic_name}</div>
            <div><strong>適用：</strong>${dis.map(x=>dn(x)).join('、')||'—'}</div>
            <div><strong>審查：</strong>${d.prior_auth?'需事前審查':'免事前審查'}</div>
          </div>
          <div class="back-btns">
            <button class="back-btn" onclick="event.stopPropagation();unflipC(${d.id})">返回</button>
            <button class="back-btn primary" onclick="event.stopPropagation();showDet(${d.id})">詳細資料</button>
          </div>
        </div>
      </div>
    </div>`;
  }).join('');
}

function flipC(id){
  const el=document.getElementById('fp-'+id);
  if(!el) return;
  const front=el.querySelector('.drug-flip-front');
  const back=el.querySelector('.drug-flip-back');
  const h=Math.max(front?.scrollHeight||130, back?.scrollHeight||130, 130);
  el.style.height=h+'px';
  el.classList.add('flipped');
}
function unflipC(id){document.getElementById('fp-'+id)?.classList.remove('flipped');}

function getUMg(pu){const m=(pu||'').match(/(\d+(?:\.\d+)?)\s*mg/i);return m?parseFloat(m[1]):1;}

function showDet(id){
  const d=_HD.find(x=>x.id===id);
  if(!d) return;
  let nfo=null;
  try{nfo=typeof d.dosage_info==='string'?JSON.parse(d.dosage_info):d.dosage_info;}catch(e){}
  const dis=d.clinical_tags?.disease||[];
  const mols=[];
  if(d.clinical_tags?.btk) mols.push('BTK抑制劑');
  if(d.clinical_tags?.cd20) mols.push('Anti-CD20');
  if(d.clinical_tags?.flt3) mols.push('FLT3抑制劑');
  if(d.clinical_tags?.ph_positive) mols.push('Ph+/BCR-ABL適用');
  if(d.clinical_tags?.bcl2) mols.push('BCL-2抑制劑');
  const rmap={'oral':'口服','iv':'靜脈注射','sc':'皮下注射','sc_iv':'皮下/靜脈','oral_or_iv':'口服或靜脈'};
  const route=rmap[nfo?.type]||'';
  const indic=(d.indication||'').split('|').map(s=>s.trim()).filter(Boolean);
  const conds=(d.conditions||'').split('|').map(s=>s.trim()).filter(Boolean);
  const uMg=getUMg(d.price_unit||'');
  const p=d.nhi_price||0;
  const srcLine=lineSrcTag(d.therapy_line_source||'待確認');

  // 資料缺漏警告框
  const warnBox=d.data_note?`<div class="data-warn"><strong>資料缺漏警告</strong>${d.data_note}</div>`:'';

  // 費用試算
  let cHtml='';
  if(nfo?.dose_per_bsa){
    const defDays=nfo.schedule?parseInt(nfo.schedule):1;
    cHtml=`<div class="calc-box"><div class="calc-title">&#128176; 費用試算（每療程周期） <span style="font-size:.7rem;font-weight:400;color:var(--heme-light)">來源：健保藥價基準 115/4/1</span></div>
      <div class="calc-row"><span class="calc-label">BSA</span><input class="calc-input" id="cB${id}" type="number" value="1.7" step="0.1" min="0.5" max="3"><span class="calc-unit">m²</span></div>
      <div class="calc-row"><span class="calc-label">劑量</span><input class="calc-input" id="cD${id}" type="number" value="${nfo.dose_per_bsa}" step="1"><span class="calc-unit">${nfo.unit||'mg/m²'}</span></div>
      <div class="calc-row"><span class="calc-label">天數</span><input class="calc-input" id="cDy${id}" type="number" value="${defDays}" step="1" min="1"><span class="calc-unit">天/周期</span></div>
      <button class="calc-btn" onclick="cBSA(${id},${p},${uMg})">計算</button>
      <div id="cR${id}" class="calc-result" style="display:none"></div></div>`;
  } else if(nfo?.dose_per_kg){
    cHtml=`<div class="calc-box"><div class="calc-title">&#128176; 費用試算（每次給藥） <span style="font-size:.7rem;font-weight:400;color:var(--heme-light)">來源：健保藥價基準 115/4/1</span></div>
      <div class="calc-row"><span class="calc-label">體重</span><input class="calc-input" id="cW${id}" type="number" value="60" step="1"><span class="calc-unit">kg</span></div>
      <div class="calc-row"><span class="calc-label">劑量</span><input class="calc-input" id="cKD${id}" type="number" value="${nfo.dose_per_kg}" step="0.1"><span class="calc-unit">${nfo.unit||'mg/kg'}</span></div>
      <button class="calc-btn" onclick="cKG(${id},${p},${uMg})">計算</button>
      <div id="cR${id}" class="calc-result" style="display:none"></div></div>`;
  } else if(nfo?.dose_fixed){
    const defD=nfo.schedule?parseInt(nfo.schedule):28;
    cHtml=`<div class="calc-box"><div class="calc-title">&#128176; 費用試算（口服療程） <span style="font-size:.7rem;font-weight:400;color:var(--heme-light)">來源：健保藥價基準 115/4/1</span></div>
      <div class="calc-row"><span class="calc-label">每日劑量</span><input class="calc-input" id="cFD${id}" type="number" value="${nfo.dose_fixed}" step="1"><span class="calc-unit">${nfo.unit||'mg'}/日</span></div>
      <div class="calc-row"><span class="calc-label">天數</span><input class="calc-input" id="cFDy${id}" type="number" value="${defD}" step="1" min="1"><span class="calc-unit">天</span></div>
      <button class="calc-btn" onclick="cFix(${id},${p},${uMg})">計算</button>
      <div id="cR${id}" class="calc-result" style="display:none"></div></div>`;
  }

  document.getElementById('detC').innerHTML=`
    <div class="modal-header">
      <div class="modal-icon">${ini(d.generic_name)}</div>
      <div style="flex:1"><div class="modal-title">${d.generic_name}</div>
        <div class="modal-subtitle">${d.trade_names||'(通用名)'} &middot; ${dis.map(x=>dn(x)).join('/')}</div></div>
      <button class="modal-close" onclick="closeDet()">&#x2715;</button>
    </div>
    <div class="modal-body">
      ${warnBox}
      <div class="detail-section"><dl>
        <div class="detail-row"><dt>適用疾病</dt><dd>${dis.map(x=>dn(x)).join('、')||'—'}</dd></div>
        ${mols.length?`<div class="detail-row"><dt>分子標記</dt><dd>${mols.join('、')}</dd></div>`:''}
        <div class="detail-row">
          <dt>治療線</dt>
          <dd>第 ${d.therapy_line||1} 線 ${srcLine}</dd>
        </div>
        <div class="detail-row"><dt>健保審查</dt><dd>${d.prior_auth?'<span style="color:var(--auth)">&#9888; 需事前審查</span>':'<span style="color:var(--nhi)">&#10003; 免事前審查</span>'}</dd></div>
        ${route?`<div class="detail-row"><dt>給藥途徑</dt><dd>${route}</dd></div>`:''}
        ${nfo?.note?`<div class="detail-row"><dt>建議劑量</dt><dd>${nfo.note}</dd></div>`:''}
        <div class="detail-row">
          <dt>健保單價</dt>
          <dd><strong>NT$${p.toLocaleString()}</strong> / ${d.price_unit||'unit'} <span class="src-tag src-nhi">健保藥價基準 115/4/1</span></dd>
        </div>
        <div class="detail-row">
          <dt>台大醫院藥價</dt>
          <dd><span style="color:var(--text-muted);font-size:.78rem">尚未建檔</span></dd>
        </div>
      </dl></div>
      <hr class="detail-divider">
      ${indic.length?`<div class="detail-section">
        <div class="section-hd">
          <span class="section-hd-label">健保給付適應症</span>
          <span class="src-tag src-nhi">全民健康保險藥物給付項目及支付標準</span>
        </div>
        <ul class="cond-list">${indic.map(l=>`<li>${l}</li>`).join('')}</ul>
      </div>`:''}
      ${conds.length?`<div class="detail-section">
        <div class="section-hd">
          <span class="section-hd-label">給付條件 / 事前審查要點</span>
          <span class="src-tag src-nhi">全民健康保險藥物給付項目及支付標準</span>
        </div>
        <ul class="cond-list">${conds.map(l=>`<li>${l}</li>`).join('')}</ul>
      </div>`:''}
      ${cHtml}
    </div>`;
  document.getElementById('detModal').classList.add('open');
}

function closeDet(){document.getElementById('detModal').classList.remove('open');}

function showRes(id,tot,units,p,cost){
  const el=document.getElementById('cR'+id);
  if(!el) return;
  el.style.display='block';
  el.innerHTML=`總量 ${tot.toFixed(0)} mg &#8594; ${units} 瓶/粒 &#215; NT$${p.toLocaleString()} = <span>NT$${cost.toLocaleString()}</span>`;
}
function cBSA(id,p,uMg){
  const bsa=+document.getElementById('cB'+id).value||1.7;
  const dose=+document.getElementById('cD'+id).value||0;
  const days=+document.getElementById('cDy'+id).value||1;
  const tot=dose*bsa*days;const v=Math.ceil(tot/uMg);showRes(id,tot,v,p,v*p);
}
function cKG(id,p,uMg){
  const wt=+document.getElementById('cW'+id).value||60;
  const dose=+document.getElementById('cKD'+id).value||0;
  const tot=dose*wt;const v=Math.ceil(tot/uMg);showRes(id,tot,v,p,v*p);
}
function cFix(id,p,uMg){
  const daily=+document.getElementById('cFD'+id).value||0;
  const days=+document.getElementById('cFDy'+id).value||28;
  const tot=daily*days;const v=Math.ceil(tot/uMg);showRes(id,tot,v,p,v*p);
}

function showCL(){document.getElementById('clModal').classList.add('open');}
function closeCL(){document.getElementById('clModal').classList.remove('open');}

document.addEventListener('DOMContentLoaded',()=>{renderSidebar();renderCards();});
"""

JS = JS_TEMPLATE.replace('DRUGDATA', inline_json)

# ── HTML ──────────────────────────────────────────────────────────────────────

HTML = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>健保血液腫瘤藥物查詢系統</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header class="header">
  <div>
    <div class="header-title">&#129978; 健保血液腫瘤藥物查詢</div>
    <div class="header-sub">Hematology Oncology NHI Drug Reference</div>
  </div>
  <div class="header-badge" onclick="showCL()">藥價基準 115/04/01 &#65372; v1.1</div>
</header>

<div class="mobile-filter-bar" id="mobFilt"></div>

<div class="layout">
  <aside class="sidebar">
    <div class="sidebar-section">
      <div class="sidebar-label">疾病分類</div>
      <div id="dFilt"></div>
    </div>
    <div class="sidebar-section">
      <div class="sidebar-label">分子標記</div>
      <div class="mol-filter" id="mFilt"></div>
    </div>
    <div class="sidebar-section">
      <div class="sidebar-label">治療線</div>
      <div id="lFilt"></div>
    </div>
  </aside>
  <main class="main">
    <div class="search-wrap">
      <input class="search-input" type="text" id="sIn" placeholder="搜尋藥物名稱、適應症..." oninput="renderCards()">
      <span class="result-count" id="rCnt"></span>
    </div>
    <div class="cards-grid" id="cGrid"></div>
  </main>
</div>

<!-- Detail Modal -->
<div class="modal-overlay" id="detModal" onclick="if(event.target===this)closeDet()">
  <div class="modal" id="detC"></div>
</div>

<!-- Changelog Modal -->
<div class="modal-overlay" id="clModal" onclick="if(event.target===this)closeCL()">
  <div class="modal">
    <div class="modal-header">
      <div class="modal-icon">&#128203;</div>
      <div><div class="modal-title">版本更新紀錄</div><div class="modal-subtitle">Changelog</div></div>
      <button class="modal-close" onclick="closeCL()">&#x2715;</button>
    </div>
    <div class="modal-body">
      <div class="cl-version">
        <div class="cl-ver-badge">v1.1 &#8212; 2026/04</div>
        <ul class="cl-items">
          <li>資料完整性政策：所有欄位必須附帶來源標籤（健保規定 / NCCN / 待確認）</li>
          <li>移除虛構的適應症文字（Dexamethasone、Doxorubicin、Rituximab、Thalidomide、Oxaliplatin）</li>
          <li>新增「資料缺漏警告」標示，明確說明哪些藥品的健保登載文字不符血液腫瘤科適應症</li>
          <li>台大醫院藥價：本工具目前無血液腫瘤科台大藥局資料，顯示「尚未建檔」</li>
          <li>治療線校正（依健保給付規定文字）：Brentuximab vedotin L2&#8594;L1；Carfilzomib L1&#8594;L2；Elotuzumab L1&#8594;L3；Pomalidomide L1&#8594;L3</li>
          <li>治療線來源標籤校正：骨幹化療藥物（Cyclophosphamide、Dexamethasone、Doxorubicin、Oxaliplatin、Vinblastine）標記 NCCN；Rituximab、Thalidomide 標記「待確認」</li>
          <li>費用試算器顯示健保藥價基準日期（115/04/01）</li>
        </ul>
      </div>
      <div class="cl-version">
        <div class="cl-ver-badge">v1.0 &#8212; 2026/04</div>
        <ul class="cl-items">
          <li>建立血液腫瘤藥物獨立查詢系統（獨立部署）</li>
          <li>收錄 30 種血液腫瘤常用藥物（健保給付），已去除品牌名重複條目</li>
          <li>疾病分類篩選：CLL、淋巴瘤、多發性骨髓瘤、CML、AML、MDS、ALL</li>
          <li>分子標記篩選：BTK抑制劑、Anti-CD20、FLT3、Ph+/BCR-ABL、BCL-2</li>
          <li>藥物翻轉卡片 + 詳細資料 Modal + 費用試算器</li>
          <li>健保藥價資料：115/04/01 公告</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<script>{JS}</script>
</body>
</html>"""

out_path = 'D:/新增資料夾/Git_NHI_Drug_Caculator/NHI_Heme_Calculator/index.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"Done: {len(HTML):,} chars, {len(HTML.splitlines())} lines")

# 列出 data_note 藥品清單做最終確認
print("\n資料缺漏警告藥品：")
for d in drugs:
    if d.get('data_note'):
        print(f"  {d['generic_name']} ({d['trade_names']}) - id={d['id']}")

print("\n治療線來源摘要：")
from collections import Counter
src_count = Counter(d.get('therapy_line_source','?') for d in drugs)
for src, cnt in src_count.items():
    print(f"  {src}: {cnt} 種")
