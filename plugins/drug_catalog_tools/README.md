# Drug Catalog Tools

這組工具處理三件事：

- 人工主檔確認欄位
- 同藥不同劑量 / formulation 結構
- 常見處方與劑量 / 藥價計算

## 主要概念

每筆藥物主檔現在可帶：

- `manual_review`
  - 人工確認正確性、主劑型是否核對、處方映射是否核對
- `formulations`
  - 同一藥的不同劑量與價格
- `dosing_profiles`
  - 固定劑量 / BSA / 體重 / AUC 的常見用法
- `common_regimen_refs`
  - 對應常見 regimen，如 `r-chop`、`br`、`aza-ven`、`vrd`

## Python 用法

```python
from plugins.drug_catalog_tools import attach_catalog_scaffold, calculate_course_cost

drug = attach_catalog_scaffold(drug)
profile = drug["dosing_profiles"][0]
result = calculate_course_cost(
    drug,
    profile,
    weight_kg=70,
    height_cm=170,
    cycles=6,
    pricing="nhi_price",
)
print(result)
```

## 支援的劑量模式

- `fixed_daily`
- `bsa`
- `weight`
- `auc`

`auc` 範例：

```python
profile = {
    "profile_id": "auc-example",
    "dose_mode": "auc",
    "dose_value": 0,
    "dose_unit": "mg",
}

result = calculate_course_cost(
    drug,
    profile,
    gfr=62,
    target_auc=5,
    cycles=1,
)
```

## 已內建的 common regimens

- `r-chop`
- `br`
- `aza-ven`
- `vrd`
