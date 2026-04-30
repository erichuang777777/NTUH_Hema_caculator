# NHI Open Data Updater Plugin

可攜式健保藥價與給付規定更新模組。

這個資料夾可以單獨複製到其他 Python 專案使用，不依賴本專案其他檔案。

你有兩種放法：

- 保留在 `plugins/nhi_open_data_updater/` 底下：
  - CLI: `python -m plugins.nhi_open_data_updater`
  - import: `from plugins.nhi_open_data_updater import NhiOpenDataUpdater`
- 只複製 `nhi_open_data_updater/` 到新專案根目錄：
  - CLI: `python -m nhi_open_data_updater`
  - import: `from nhi_open_data_updater import NhiOpenDataUpdater`

## 功能

- 下載健保開放資料 `A21030000I-E41001-001`
- 依 `generic_name` 比對官方藥品資料
- 回寫：
  - `nhi_open_data`
  - `nhi_drug_codes`
  - `nhi_pay_codes`
  - `nhi_pay_pdf_urls`
  - `nhi_pay_pdf_filenames`
  - `nhi_pay_last_updated`
  - `nhi_rule_text`
  - `nhi_price`

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
python -m plugins.nhi_open_data_updater --data ./drugs.json --pdf-cache-dir ./nhi_pdfs
python -m plugins.nhi_open_data_updater --data ./drugs.json --drug Acalabrutinib --pdf-cache-dir ./nhi_pdfs
python -m plugins.nhi_open_data_updater --data ./drugs.json --output ./drugs.updated.json --skip-pdf
```

## Python import 用法

```python
from plugins.nhi_open_data_updater import NhiOpenDataUpdater, load_json_records, save_json_records

records = load_json_records("drugs.json")
updater = NhiOpenDataUpdater()
result = updater.update_records(
    records,
    selected_drugs=["Acalabrutinib", "Venetoclax"],
    pdf_cache_dir="nhi_pdfs",
)
save_json_records("drugs.updated.json", records)
print(result)
```

## 常見整合方式

```python
from plugins.nhi_open_data_updater import NhiOpenDataUpdater

updater = NhiOpenDataUpdater()
result = updater.update_file(
    data_path="data/drugs.json",
    output_path="data/drugs.json",
    pdf_cache_dir="data/nhi_pdfs",
)
```

## 依賴

- `requests`
- `PyMuPDF` (`fitz`)
