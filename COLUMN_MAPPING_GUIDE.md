# Excel Template Column Mapping Guide

## Overview

The **Column Mapping approach** is an intelligent Excel template filling method that automatically detects your template structure and fills data without requiring any placeholder syntax. Simply create an Excel file with period headers and metric names, and the system will automatically map and fill the data.

## How It Works

The column mapping system works in four steps:

### 1. Company Name Detection (Row 1)

The system checks for a company name placeholder in merged cells B1:E1:

**Supported Formats:**

- `COMPANY_NAME_PLACEHOLDER` - replaced with actual company name
- Any text containing "company_name" - replaced with actual company name
- Empty merged cells - filled with company name

### 2. Period Detection (Row 2 - Headers)

The system scans Row 2 (or first 5 rows) to find period headers:

**Supported Formats:**

- Direct dates with suffix: `30.06.2025 Q`, `31.03.2025 Y`
- Just dates: `30.06.2025` (assumes quarterly)
- Quarter labels: `Q1 FY2026`, `Q2 2025`
- Year labels: `FY 2025`, `Year 2025`

**Examples:**

```
Row 1:  [A1 empty] | [B1:E1 merged] COMPANY_NAME_PLACEHOLDER
Row 2:  Metric     | 30.06.2025 Q    | 31.03.2025 Q    | 30.06.2024 Q
```

The system will parse:

- B1:E1 merged cell → Company name
- `30.06.2025 Q` → `30.06.2025` (quarterly)
- `31.03.2025 Y` → `31.03.2025_Y` (yearly)

### 3. Metric Detection (Column A from Row 3)

The system scans Column A starting from Row 3 (row after header) to find metric names:

**Supported Metrics (with fuzzy matching):**

**Revenue Section:**

- Sale of Goods / Sale of Products
- Export Sales
- Service Revenue
- Other Operating Revenue/Revenues
- Revenue from Operations / Total Revenue
- Other Income
- Total Income

**Expenses:**

- Cost of Materials Consumed
- Excise Duty
- Purchases Stock in Trade
- Changes in Inventories
- Employee Benefits Expense
- Finance Costs
- Depreciation and Amortisation
- Other Expenses
- Advertising Expense
- Impairment Losses
- Total Expenses

**Profit & Tax:**

- Profit Before Exceptional Items and Tax
- Exceptional Items
- Profit Before Tax
- Current Tax / Total Tax Expense
- Net Profit / Profit for the Period

**Other:**

- Other Comprehensive Income
- Total Comprehensive Income
- Paid-up Equity Share Capital
- Other Equity
- EPS Basic / EPS (Basic)
- EPS Diluted / EPS (Diluted)

### 4. Data Filling

For each matched metric and detected period, the system:

1. Looks up the value in your data
2. Formats it with Indian number formatting
3. Fills the intersection cell (e.g., B2, C2, etc.)

## Template Structure

### Basic Template

```excel
Row 1:  [A1 empty]              | [B1:E1 merged] COMPANY NAME
Row 2:  Metric                  | 30.06.2025 Q | 31.03.2025 Q | 30.06.2024 Q | 31.03.2025 Y
Row 3:  Sale of Goods           |              |              |              |
Row 4:  Export Sales            |              |              |              |
Row 5:  Revenue from Operations |              |              |              |
Row 6:  Net Profit              |              |              |              |
```

**After Processing:**

```excel
Row 1:  [A1 empty]              | [B1:E1 merged] TEST COMPANY
Row 2:  Metric                  | 30.06.2025 Q | 31.03.2025 Q | 30.06.2024 Q | 31.03.2025 Y
Row 3:  Sale of Goods           |   15,000.50  |   14,500.25  |   13,200.75  |   58,000.00
Row 4:  Export Sales            |    5,000.00  |    4,800.00  |    4,500.00  |   19,000.00
Row 5:  Revenue from Operations |   25,000.00  |   24,000.00  |   22,000.00  |   95,000.00
Row 6:  Net Profit              |    2,500.00  |    2,300.00  |    2,100.00  |    9,500.00
```

## Using via Streamlit UI

1. Go to the **"AI Analysis"** tab
2. Upload your financial data JSON or use an existing parse result
3. Upload your Excel template (`.xlsx` or `.xls`)
4. Click **"Generate Excel using AI & Template"**
5. Download the filled Excel file

## Using via API

### Request

```bash
POST /api/generate-excel-ai
Content-Type: multipart/form-data

Fields:
  company_name: BRITANNIA
  document_name: Britannia_Q2_2025
  template_excel: <your_excel_file>
  preferred_format: excel
  save: true
```

### Python Example

```python
import requests

url = "http://localhost:5000/api/generate-excel-ai"

files = {
    'template_excel': ('my_template.xlsx', open('my_template.xlsx', 'rb'),
                      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
}

data = {
    'company_name': 'BRITANNIA',
    'document_name': 'Britannia_Q2_2025',
    'preferred_format': 'excel',
    'save': 'true'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## Column Mapping vs Placeholder Mode

The system automatically tries both modes:

### **Column Mapping Mode** (Recommended)

- ✅ No syntax required
- ✅ Intuitive Excel layout
- ✅ Standard format with headers
- ✅ Fuzzy metric matching (typo-tolerant)
- ⚠️ Requires structured layout (headers in row 1, metrics in column A)

### **Placeholder Mode** (Legacy)

- ✅ Flexible placement anywhere in template
- ✅ Works with complex layouts
- ✅ Can embed data in text: "Revenue is {{revenue[30.06.2025]}}"
- ⚠️ Requires learning placeholder syntax
- ⚠️ Error-prone (typos in keys)

**System Behavior:**

1. Try Column Mapping first
2. If no structure detected, fallback to Placeholder mode
3. If neither works, return template unchanged

## Fuzzy Matching

The system uses **80% similarity threshold** for metric matching:

**Examples that match:**

- "Sale of Goods" ✅ matches "sale_of_goods"
- "Export Sales" ✅ matches "export_sales"
- "Profit Before Tax" ✅ matches "profit_before_tax"
- "EPS Basic" ✅ matches "eps_basic"
- "Emp Benefits Expense" ✅ matches "employee_benefits_expense" (score: 85%)

**Examples that don't match:**

- "Revenue" ❌ too generic (multiple matches)
- "Profit" ❌ ambiguous (PBT vs Net Profit)

**Best Practice:** Use full metric names from the supported list above.

## Creating Your Own Template

### Step 1: Company Name Row

- Row 1, Column A: Leave empty or add label
- Row 1, Columns B-E: Merge cells and add `COMPANY_NAME_PLACEHOLDER`

```excel
A1: [empty]    B1:E1 (merged): COMPANY_NAME_PLACEHOLDER
```

### Step 2: Set Up Headers

- Row 2, Column A: "Metric" (or leave blank)
- Row 2, Columns B onwards: Period headers

```excel
A2: Metric    B2: 30.06.2025 Q    C2: 31.03.2025 Q    D2: 30.06.2024 Q
```

### Step 3: Add Metrics

- Starting from Row 3, Column A: Add metric names

```excel
A3: Sale of Goods
A4: Export Sales
A5: Revenue from Operations
```

### Step 4: Optional Formatting

- Bold headers (Row 2)
- Add borders
- Set column widths
- Color the header row
- Style the company name row

### Step 5: Upload and Generate

The system will:

- Detect your structure automatically
- Match metric names to data keys
- Fill intersection cells with formatted values
- Preserve your formatting

## Advanced Features

### Multiple Sheets

The system processes **all sheets** in your workbook:

- Each sheet is scanned independently
- Column mapping applied if structure is detected
- Fallback to placeholder mode if needed

### Custom Periods

Support for custom date formats:

- `DD.MM.YYYY Q` for quarterly periods
- `DD.MM.YYYY Y` for yearly periods
- Quarter labels (Q1-Q4) with fiscal year
- Financial year labels (FY 2025)

### Preserving Formatting

The system preserves:

- Cell styles (fonts, colors, borders)
- Column widths
- Row heights
- Merged cells
- Formulas (in cells without data)

## Troubleshooting

### No Data Filled

**Symptom:** Template returned unchanged

**Possible Causes:**

1. ❌ No period headers found in Row 2 (or first 5 rows)
   - **Fix:** Put period headers in Row 2, Column B onwards
2. ❌ Metric names don't match
   - **Fix:** Use full names from supported list
   - **Debug:** Check logs for "No match found" messages
3. ❌ Period format not recognized
   - **Fix:** Use supported formats (DD.MM.YYYY Q/Y)
4. ❌ Data keys don't match template metrics

   - **Fix:** Verify your data has the correct keys

5. ❌ Company name not in Row 1, merged cells B1:E1
   - **Fix:** Merge cells B1:E1 and add placeholder text

### Partial Data Filled

**Symptom:** Some cells filled, others empty

**Possible Causes:**

1. ⚠️ Some metric names didn't match (fuzzy score < 80%)
   - **Check:** Debug logs show which metrics matched
2. ⚠️ Data missing for some periods
   - **Expected:** System puts `-` for zero/missing values
3. ⚠️ Period format varies across columns
   - **Fix:** Use consistent format for all period headers

### Wrong Values

**Symptom:** Numbers don't match expected data

**Possible Causes:**

1. ❌ Metric matched to wrong key
   - **Check:** Debug logs show matched key
   - **Fix:** Use more specific metric name
2. ❌ Period parsed incorrectly
   - **Check:** Debug logs show parsed period
   - **Fix:** Use explicit date format

## Logging and Debug

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Key Log Messages

```
INFO: Filled company name in merged cell B1: TEST COMPANY
INFO: Found header row at row 2 with 4 periods: {'B': '30.06.2025', 'C': '31.03.2025', ...}
DEBUG: Header row: 2, Metrics start row: 3
DEBUG: Row 3: Checking metric 'Sale of Goods'
DEBUG:   -> Matched to key: sale_of_goods
DEBUG:   -> Filled B3 with 15,000.50 (key=sale_of_goods, period=30.06.2025)
INFO: Column mapping filled 20 cells
```

### Response Metadata

```json
{
  "success": true,
  "message": "Excel generated using column mapping approach",
  "data": {
    "file_path": "excel_storage/abc123.xlsx",
    "mode_used": "column_mapping",
    "cells_filled": 20
  }
}
```

## Sample Templates

### Financial Summary Template

Location: `templates/financial_summary_template_column_mapping.xlsx`

Features:

- Row 1: Company name in merged cells (B1:E1)
- Row 2: Headers - 4 period columns (Q2 FY2026, Q1 FY2026, Q2 FY2025, FY2025)
- Row 3+: 25 common financial metrics
- Formatted headers with colors
- Professional styling with borders

### Create Your Own

Copy the sample template and:

1. Modify company name placeholder in Row 1
2. Modify period headers in Row 2 for your fiscal year
3. Add/remove metric rows as needed (starting from Row 3)
4. Customize formatting and branding
5. Upload and test

## Best Practices

1. **Use Full Metric Names:** "Revenue from Operations" not "Revenue"
2. **Consistent Period Format:** Use same format across all columns in Row 2
3. **Header in Row 2:** System scans first 5 rows but Row 2 is most reliable
4. **Metrics in Column A:** Starting from Row 3 (after header row)
5. **Company Name in Row 1:** Merge B1:E1 and use placeholder text
6. **Test with Sample Data:** Verify structure before production use
7. **Check Debug Logs:** Understand what was matched
8. **Preserve Formatting:** System keeps your styles intact

## Migration from Placeholder Mode

### Old Template (Placeholder)

```excel
A1: Company: {{company_name}}
A2: Metric               B2: Q1 FY2026
A3: Sale of Goods        B3: {{sale_of_goods[30.06.2025]}}
A4: Export Sales         B4: {{export_sales[30.06.2025]}}
```

### New Template (Column Mapping)

```excel
A1: Metric               B1: 30.06.2025 Q
A2: Sale of Goods
A3: Export Sales
```

**Migration Steps:**

1. Remove all `{{}}` placeholders
2. Move periods from placeholder keys to header row
3. Keep only metric names in Column A
4. System handles the rest automatically

**Benefits:**

- 90% less syntax
- Easier for non-technical users
- More maintainable
- Same or better performance

## Limitations

1. **Metric Matching:** Limited to predefined metric list (can be extended)
2. **Header Detection:** Requires at least 2 periods in same row (Row 2 preferred)
3. **Column A Only:** Metric names must be in Column A (starting Row 3)
4. **First 5 Rows:** Header must be in one of the first 5 rows
5. **No Nested Structures:** Flat table format only
6. **Company Name:** Must be in merged cells B1:E1 for automatic filling

## Support

- **Documentation:** See [EXCEL_TEMPLATE_GUIDE.md](EXCEL_TEMPLATE_GUIDE.md) for placeholder mode
- **API Reference:** See [README.md](README.md) for full API documentation
- **Sample Code:** See `test_column_mapping.py` for working examples
- **Debug Mode:** Enable logging to see detailed matching process

## Version History

- **v2.3** - Column mapping feature added
- **v2.2** - Excel template support with placeholders
- **v2.1** - AI extraction with OpenAI
- **v2.0** - Initial Excel generation

---

**Next:** Try creating your own template using the sample as a reference!
