# NHI Heme Calculator v1.1
## 全民健康保險血液科藥物計算器

**獨立開發項目 — 與乳癌項目分開**

### 概況
台灣全民健康保險血液腫瘤科用藥參考工具，包含 30 種血液癌症常用藥物（CLL、淋巴瘤、骨髓瘤、CML、AML、MDS、ALL）。

### 特色
- 💊 30 種血液腫瘤藥物資料庫
- 🏥 健保給付規定 + NCCN 治療指引
- 📊 治療線分類（第一線/第二線/第三線）
- 💰 成本計算機（BSA、kg、固定劑量）
- 📱 行動裝置友善設計
- ✅ 嚴格數據完整性政策（v1.1）

### 數據完整性政策 (v1.1)
所有顯示資料必須有來源標籤：
- `健保規定` — 來自全民健康保險藥物給付項目及支付標準
- `NCCN` — 來自 NCCN 臨床實踐指南（主要用於骨髓瘤化療骨架藥物）
- `待確認` — 需要進一步驗證的項目

**禁止規則：** 不得虛構任何數據、條件或適應症。未在官方文件中記載的用途必須標記警告。

### 檔案結構
```
NHI_Heme_Calculator/
├── index.html              # 獨立網頁應用（靜態部署）
├── build_html.py           # 從 JSON 資料重建 HTML
├── netlify.toml            # Netlify 部署配置（獨立站點）
├── data/
│   ├── heme_final.json     # 已修正的 30 種藥物資料
│   ├── heme_inline.json    # 簡潔格式版本
│   ├── data_audit.txt      # 資料查核報告
│   └── therapy_line_check.txt # 治療線驗證紀錄
├── .gitignore
└── README.md
```

### 已知資料問題 (待外部驗證)
| 藥物 | 問題說明 | 狀態 |
|------|--------|------|
| Dexamethasone (1536) | NHI = Ozurdex (眼科) | 標記警告 ⚠ |
| Doxorubicin (1537) | NHI = Lipo-Dox (卵巢/乳癌) | 標記警告 ⚠ |
| Oxaliplatin (1550) | NHI = 大腸/胃癌 | 標記警告 ⚠ |
| Rituximab (1555) | NHI = RA/天疱瘡 (風濕) | 待確認 🔍 |
| Thalidomide (1558) | NHI = 痲瘋/PNH | 待確認 🔍 |

### 療法線修正 (v1.1)
以下 4 種藥物根據 NHI 官方條文進行療法線調整：

| 藥物 | 修正 | 依據 |
|------|------|------|
| Brentuximab vedotin | L2 → L1 | 文件："先前未曾接受治療" |
| Carfilzomib | L1 → L2 | 文件："先前曾接受...治療失敗" |
| Elotuzumab | L1 → L3 | 文件："曾接受過至少兩種療法" |
| Pomalidomide | L1 → L3 | 同上 |

### 部署
靜態網頁應用，無後端需求：
```bash
# 從資料 JSON 重建 HTML
python3 build_html.py

# 內容部署至 Netlify（獨立站點）
# 預計 URL: heme.nhi-calc.netlify.app （待確認）
```

### 待辦項目
- [ ] 取得官方 NHI 文件掃描件驗證 5 種問題藥物
- [ ] 搜尋 NHI 藥物給付項目中 Rituximab/Thalidomide 的腫瘤科用途
- [ ] Netlify 獨立部署設置
- [ ] 台大醫院藥價資料整合（如有來源）

### 版本歷史
- **v1.1** (2026-04-30) — 數據完整性強化、療法線修正、警告機制
- **v1.0** — 初版發布

---

**開發者筆記：** 此項目與乳癌計算器完全獨立。維護人員應定期檢視官方 NHI 文件更新，確保資料準確性。
