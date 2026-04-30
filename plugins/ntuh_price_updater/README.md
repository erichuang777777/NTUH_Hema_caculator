# NTUH Price Updater Plugin

可攜式台大醫院院內自費價更新模組。

這個資料夾可以單獨複製到其他 Python 專案使用，不依賴本專案其他檔案。

你有兩種放法：

- 保留在 `plugins/ntuh_price_updater/` 底下：
  - CLI: `python -m plugins.ntuh_price_updater`
  - import: `from plugins.ntuh_price_updater import NtuhPriceUpdater`
- 只複製 `ntuh_price_updater/` 到新專案根目錄：
  - CLI: `python -m ntuh_price_updater`
  - import: `from ntuh_price_updater import NtuhPriceUpdater`

## 功能

- 查詢台大藥劑部頁面 `QueryDrugInfoPhr.aspx`
- 依 `generic_name`、`trade_names`、`price_unit` 做比對
- 回寫：
  - `ntuh_self_pay_price`
  - `ntuh_price_unit`
  - `ntuh_open_data`

## 需要的輸入 JSON 結構

至少每筆藥物需要：

```json
[
  {
    "generic_name": "Acalabrutinib",
    "trade_names": "Calquence",
    "price_unit": "100mg/cap"
  }
]
```

## CLI 用法

```bash
python -m plugins.ntuh_price_updater --data ./drugs.json
python -m plugins.ntuh_price_updater --data ./drugs.json --drug Acalabrutinib
python -m plugins.ntuh_price_updater --data ./drugs.json --output ./drugs.updated.json
```

## Python import 用法

```python
from plugins.ntuh_price_updater import NtuhPriceUpdater, load_json_records, save_json_records

records = load_json_records("drugs.json")
updater = NtuhPriceUpdater()
result = updater.update_records(records, selected_drugs=["Acalabrutinib", "Venetoclax"])
save_json_records("drugs.updated.json", records)
print(result)
```

## 常見整合方式

```python
from plugins.ntuh_price_updater import NtuhPriceUpdater

updater = NtuhPriceUpdater()
result = updater.update_file(
    data_path="data/drugs.json",
    output_path="data/drugs.json",
)
```

## 依賴

- `requests`
- `beautifulsoup4`
