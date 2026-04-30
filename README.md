# NHI Heme Calculator v1.1
## 全民健康保險血液腫瘤藥物查詢系統

本專案為血液腫瘤科專用的靜態查詢站，整合健保藥價、健保給付條文、台大院內自費價、人工主劑型確認、常見審查摘要欄位與錯誤通報流程。部署後可離線使用；更新動作在建置期由腳本執行。

### 本階段定位
- 交付可用的 `v1.1` 靜態站點與資料更新工具
- 功能以穩定、可維護、可核對原始來源為優先
- 本階段到此收斂，後續只做 bug fix、資料修正與必要安全修補

### 目前涵蓋內容
- 30 種血液腫瘤常用藥物主檔
- 健保給付規定、治療線、事前審查提示
- 健保藥價與健保生效日
- 台大醫院院內自費價與台大查詢日
- 同成分多劑型候選整理與人工主劑型確認
- 常見 regimen、BSA / kg / 固定劑量 / 口服週期成本計算
- 指引與建議來源版本化欄位
- 錯誤通報、審核狀態與 GitHub issue 同步橋接

### 專案結構
```text
NHI_Heme_Calculator/
├── core/
│   ├── __init__.py
│   └── site_builder.py
├── specialties/
│   ├── README.md
│   └── heme/
│       ├── config.py
│       ├── postprocess.py
│       └── review_support.py
├── plugins/
│   ├── drug_catalog_tools/
│   ├── nhi_open_data_updater/
│   └── ntuh_price_updater/
├── scripts/
│   ├── add_recommendation_source_version.py
│   ├── bootstrap_specialty_catalog.py
│   ├── build_specialty_site.py
│   ├── calc_drug_cost.py
│   ├── confirm_drug_formulation.py
│   ├── create_drug_entry.py
│   ├── create_specialty_module.py
│   ├── github_issue_bridge.py
│   ├── prepare_heme_catalog.py
│   ├── refresh_heme_data.ps1
│   ├── update_nhi_open_data.py
│   └── update_ntuh_prices.py
├── data/
│   ├── common_regimens.json
│   ├── heme_drugs_clean.json
│   ├── heme_final.json
│   ├── heme_inline.json
│   ├── data_audit.txt
│   └── therapy_line_check.txt
├── build_html.py
├── index.html
├── netlify.toml
└── README.md
```

### 架構說明
- `core/`
  - 通用靜態站點 builder
  - 可供不同科別重用
- `specialties/heme/`
  - 血液科專用規則、文案、審查欄位 schema
- `plugins/`
  - 可攜式更新與主檔工具
  - 可搬到其他專案獨立使用
- `scripts/`
  - 專案層級執行入口
  - 負責更新資料、確認主劑型、計算成本、建立新科別骨架

### 執行方式
重建靜態頁：

```powershell
python build_html.py
```

完整更新健保與台大資料後重建：

```powershell
.\scripts\refresh_heme_data.ps1
```

只更新單一藥物：

```powershell
.\scripts\refresh_heme_data.ps1 -Drug Acalabrutinib
python scripts\update_nhi_open_data.py --drug Acalabrutinib --skip-pdf
python scripts\update_ntuh_prices.py --drug Acalabrutinib
```

人工鎖定主劑型：

```powershell
python scripts\confirm_drug_formulation.py --drug Cytarabine --label "500MG/vial" --verified-by TH
```

成本試算：

```powershell
python scripts\calc_drug_cost.py --drug Lenalidomide --profile-id default --cycles 1
python scripts\calc_drug_cost.py --drug Bendamustine --profile-id default --weight-kg 70 --height-cm 170 --cycles 1
```

### 更新來源與策略
- 健保主來源
  - `A21030000I-E41001-001` 健保用藥品項查詢項目檔
  - 以 Open Data API 為日常更新主來源
- 健保總表 PDF
  - 每月總表適合做人工核對與版本封存
  - 單藥 PDF 由給付章節編碼抓取，用於詳細條文追溯
- 台大院內資料
  - 以台大藥劑部查詢頁為第二資料來源
  - 與健保價分開顯示，不互相覆蓋

### 資料治理原則
- 所有重要欄位應保留來源或來源日期
- 健保價與台大院內自費價必須分開顯示
- 同成分多劑型不可自動視為同一價格
- 官方回傳 `0.00` 時不得自動當成最終正確價格，需標示待人工確認
- 疾病推論、治療線與院內建議可由系統先產生，但都應允許人工覆核

### 錯誤通報與審核流程
- 藥物卡片可直接發起錯誤通報
- 通報狀態支援 `待確認 / 已確認 / 已修正 / 已結案`
- 詳細頁可查看本機通報紀錄、審核時間軸與版本紀錄
- 若啟動本機 bridge，可直接同步 GitHub Issues

啟動本機 GitHub bridge：

```powershell
$env:GITHUB_REPO="erichuang777777/NHI_Drug_Caculator"
$env:GITHUB_TOKEN="你的 GitHub token"
python scripts\github_issue_bridge.py
```

如需讓已部署站點也能連到本機 bridge，請額外指定允許來源：

```powershell
$env:ISSUE_BRIDGE_ALLOWED_ORIGINS="https://your-site.example,https://your-preview.example"
python scripts\github_issue_bridge.py
```

### 安全原則
- 靜態頁面不內嵌 GitHub token
- GitHub Issues 寫入只經由本機 `github_issue_bridge.py`
- bridge 預設只綁定 `127.0.0.1`
- bridge 僅接受 `file://`、本機 `localhost/127.0.0.1` 頁面，以及明確列入 allowlist 的來源

### 可移植模組
以下模組可直接搬到其他專案：
- `plugins/nhi_open_data_updater`
- `plugins/ntuh_price_updater`
- `plugins/drug_catalog_tools`

若要建立新科別，建議流程：
1. 提供藥物清單
2. 執行 `bootstrap_specialty_catalog.py`
3. 建立 `specialties/<name>/`
4. 由該科使用者確認疾病分類、審查欄位、常見 regimen 與前端文案

### 已知需人工持續確認項目
| 項目 | 說明 |
|------|------|
| 部分藥物原始適應症 | 個別官方文字與血液腫瘤常用情境不完全一致，仍需臨床人工確認 |
| 多劑型藥物 | 如 Cytarabine、Azacitidine 等，主劑型與價格不可完全自動決定 |
| 台大比對命中率 | 少數藥物可能因品名或規格差異未命中，需補人工規則 |
| 指引內容 | NCCN、院內共識、學會建議需依來源與版本持續維護 |

### 本階段完成清單
- [x] 建立血液腫瘤藥物靜態查詢站
- [x] 接上健保 Open Data 更新腳本
- [x] 接上單藥給付條文 PDF 追溯
- [x] 接上台大院內自費價更新腳本
- [x] 分離健保價與台大院內自費價顯示
- [x] 建立同成分多劑型候選整理與人工確認機制
- [x] 支援常見 regimen 與劑量 / 週期 / 成本計算
- [x] 支援審查資料整理欄位與摘要輸出
- [x] 支援錯誤通報、審核狀態與本機留存
- [x] 建立 GitHub Issues bridge
- [x] 建立 `core / specialty / plugins` 可擴充架構
- [x] 支援以藥物清單 bootstrap 其他科別主檔

### 本階段範圍外與維護事項
- 官方文件與院內資料仍需定期人工抽查
- 若擴充其他癌別，建議新增對應 `specialties/<name>/` 規則層
- 後續不再主動擴功能，除非有明確臨床或維護需求

### 版本歷史
- **v1.1** `2026-04-30`
  - 健保 Open Data 更新與單藥 PDF 追溯
  - 台大院內自費價同步
  - 多劑型人工確認
  - 審查資料整理欄位
  - 錯誤通報與 GitHub Issues bridge
  - `core / specialty / plugins` 架構整理
- **v1.0**
  - 初版血液腫瘤藥物查詢站

### 維護備註
本專案目前已達可交付狀態。後續維護建議聚焦於資料正確性、少量 UI 修正、以及安全或穩定性補丁。
