# Reusable Update Plugins

這裡放的是可攜式模組，不是只給本專案用的腳本。

## 目前提供

- `plugins/nhi_open_data_updater`
  - 更新健保藥價與給付規定
  - 可下載單藥 PDF 並回寫 `nhi_rule_text`
- `plugins/ntuh_price_updater`
  - 更新台大醫院院內自費價
  - 獨立回寫 `ntuh_self_pay_price` 與 `ntuh_open_data`
- `plugins/drug_catalog_tools`
  - 補主檔 scaffold、formulation、多劑量與常見 regimen
  - 支援固定劑量 / BSA / 體重 / AUC 成本計算

## 搬到其他專案的方法

1. 直接複製整個 plugin 資料夾
2. 安裝對應依賴
3. 用 `python -m ...` 執行，或在程式裡 import

## 範例

```bash
python -m plugins.nhi_open_data_updater --data ./drugs.json --pdf-cache-dir ./nhi_pdfs
python -m plugins.ntuh_price_updater --data ./drugs.json
```
