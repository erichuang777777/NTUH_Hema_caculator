# Specialties

每個癌別或科別應以獨立模組存在 `specialties/<name>/`，負責：
- 專科 UI 文案與站點設定
- 疾病/分子標記修正規則
- 治療線人工校正規則
- 審查欄位 schema
- 專科特有的指引整合邏輯

目前已實作：
- `specialties/heme/`
  - `config.py`
  - `postprocess.py`
  - `review_support.py`

通用更新、主檔、計算與版本控制應盡量留在 `core/` 或 `plugins/`，避免癌別之間重複實作。
