# JSON Template Guide for AI Excel Generator

## Overview

The AI Excel Generator now supports **custom JSON templates** to define the structure of generated Excel files. Instead of using a fixed 47-row format, you can define your own rows (particulars) and columns (periods) using a JSON configuration file.

## Template Structure

### Basic Format

```json
{
  "title": "Financial Statement",
  "template_name": "Standard P&L",
  "columns": [
    {
      "period": "30.06.2025",
      "label": "Q1 FY2026",
      "description": "3M-30th Jun 2025"
    }
  ],
  "rows": [
    {
      "type": "section_header",
      "label": "REVENUE",
      "key": ""
    },
    {
      "type": "data",
      "label": "Sale of goods",
      "key": "sale_of_goods"
    }
  ],
  "formatting": {
    "section_header": {
      "bold": true,
      "background_color": "D3D3D3"
    }
  },
  "layout": {
    "title_row": 1,
    "period_header_row": 2,
    "data_start_row": 3
  }
}
```

### Columns Array

Defines the **periods** (dates) that appear in **Row 1** of the Excel file.

**Fields:**

- `period` (string, required): The period key used to match data (e.g., `"30.06.2025"`, `"31.03.2025_Y"`)
- `label` (string, required): Display label in Excel header (e.g., `"Q1 FY2026"`, `"FY 2025"`)
- `description` (string, optional): Additional description (e.g., `"3M-30th Jun 2025"`)

**Example:**

```json
"columns": [
  {"period": "30.06.2025", "label": "Q1 FY2026", "description": "3M-30th Jun 2025"},
  {"period": "30.06.2024", "label": "Q1 FY2025", "description": "3M-30th Jun 2024"},
  {"period": "31.03.2025_Y", "label": "FY 2025", "description": "12M-31st Mar 2025"}
]
```

### Rows Array

Defines the **particulars** (metric names) that appear in **Column A** of the Excel file.

**Fields:**

- `type` (string, required): Row type - one of:
  - `"section_header"`: Section title (e.g., "REVENUE", "EXPENSES")
  - `"data"`: Data row with values
  - `"total"`: Total/subtotal row (bold formatting)
  - `"metric"`: Calculated metric row
  - `"blank"`: Empty row for spacing
- `label` (string, required): Display text in Column A
- `key` (string, optional): Data key for matching extracted values (required for `"data"` type)

**Example:**

```json
"rows": [
  {"type": "section_header", "label": "REVENUE", "key": ""},
  {"type": "data", "label": "Sale of goods", "key": "sale_of_goods"},
  {"type": "data", "label": "Export sales", "key": "export_sales"},
  {"type": "total", "label": "Total Revenue", "key": "revenue_from_operations"},
  {"type": "blank", "label": "", "key": ""}
]
```

### Formatting Object

Defines styling rules for different row types.

**Supported Fields:**

- `bold` (boolean): Make text bold
- `background_color` (string): Hex color code (without #) - e.g., `"D3D3D3"` for light gray
- `font_size` (number): Font size in points

**Example:**

```json
"formatting": {
  "section_header": {
    "bold": true,
    "background_color": "D3D3D3",
    "font_size": 11
  },
  "total": {
    "bold": true,
    "background_color": "E8E8E8"
  },
  "metric": {
    "bold": true
  }
}
```

### Layout Object

Defines row positions for different sections.

**Fields:**

- `title_row` (number): Row number for company name title (default: 1)
- `period_header_row` (number): Row number for period headers (default: 2)
- `data_start_row` (number): First row for data (default: 3)

## How It Works

### Excel Structure

The generated Excel file has this structure:

```
Row 1: [Company Name Title - spans all columns]
Row 2: [Particulars] | [Period 1] | [Period 2] | [Period 3] | ...
Row 3: [Row 1 Label]  | [Value]    | [Value]    | [Value]    | ...
Row 4: [Row 2 Label]  | [Value]    | [Value]    | [Value]    | ...
...
```

### Data Matching

For each data row:

1. The `key` from the row specification matches the AI-extracted data
2. The `period` from the column specification matches the date key in extracted data
3. The cell is filled with: `extracted_data[row.key][column.period]`

**Example:**

```json
// Template
{"type": "data", "label": "Sale of goods", "key": "sale_of_goods"}
{"period": "30.06.2025", "label": "Q1 FY2026"}

// Extracted Data
{
  "sale_of_goods": {
    "30.06.2025": 123456789.50
  }
}

// Result in Excel
Cell B3: ₹1,234.57 Lakhs (formatted)
```

## Using JSON Templates

### In Streamlit UI

1. Navigate to **AI Excel Generator** tab
2. Expand **Custom Excel Template (JSON Format)** section
3. Upload your JSON template file
4. Review the template preview showing columns and rows count
5. Click **Generate Excel** - the template will be used automatically

### Via API

**Endpoint:** `POST /api/generate-excel-ai`

**With Template (multipart request):**

```python
import requests

files = {
    'template_json': open('my_template.json', 'rb')
}
data = {
    'data': json.dumps({
        'company_name': 'BRITANNIA',
        'document_name': 'Britannia_Unaudited_Q2_June_2026',
        'preferred_format': 'html',
        'save': False
    })
}

response = requests.post(
    'http://localhost:5000/api/generate-excel-ai',
    files=files,
    data=data
)
```

**Without Template (standard JSON):**

```python
response = requests.post(
    'http://localhost:5000/api/generate-excel-ai',
    json={
        'company_name': 'BRITANNIA',
        'document_name': 'Britannia_Unaudited_Q2_June_2026',
        'preferred_format': 'html'
    }
)
```

## Default Template

A default template is provided at `excel_template_default.json` with:

- **11 columns** covering common quarterly and yearly periods
- **47 rows** matching the original fixed format
- Standard P&L structure (Revenue → Expenses → Profit)

You can use this as a starting point for creating custom templates.

## Template Examples

### Minimal Quarterly Report

```json
{
  "title": "Quarterly Financial Report",
  "template_name": "Minimal Quarterly",
  "columns": [
    { "period": "30.06.2025", "label": "Q1 FY2026" },
    { "period": "30.06.2024", "label": "Q1 FY2025" }
  ],
  "rows": [
    { "type": "section_header", "label": "REVENUE" },
    {
      "type": "data",
      "label": "Total Revenue",
      "key": "revenue_from_operations"
    },
    { "type": "blank", "label": "" },
    { "type": "section_header", "label": "PROFIT" },
    { "type": "data", "label": "Net Profit", "key": "profit_for_the_period" }
  ],
  "formatting": {
    "section_header": { "bold": true, "background_color": "4472C4" },
    "data": { "bold": false }
  },
  "layout": {
    "title_row": 1,
    "period_header_row": 2,
    "data_start_row": 3
  }
}
```

### Custom Metrics Focus

```json
{
  "title": "Key Performance Indicators",
  "template_name": "KPI Dashboard",
  "columns": [
    { "period": "30.06.2025", "label": "Q1 2025" },
    { "period": "31.03.2025", "label": "Q4 2024" },
    { "period": "31.12.2024", "label": "Q3 2024" }
  ],
  "rows": [
    { "type": "metric", "label": "Revenue Growth %", "key": "revenue_growth" },
    { "type": "metric", "label": "EBITDA Margin %", "key": "ebitda_margin" },
    {
      "type": "metric",
      "label": "Net Profit Margin %",
      "key": "net_profit_margin"
    },
    { "type": "metric", "label": "EPS (₹)", "key": "earnings_per_share" }
  ],
  "formatting": {
    "metric": { "bold": true, "background_color": "FFF2CC" }
  }
}
```

## Best Practices

### 1. Consistent Period Keys

Use the same period format throughout your template and ensure they match the extracted data keys.

**Good:**

```json
"columns": [
  {"period": "30.06.2025", "label": "Q1 FY2026"},
  {"period": "31.03.2025_Y", "label": "FY 2025"}
]
```

**Bad (inconsistent):**

```json
"columns": [
  {"period": "30.06.2025", "label": "Q1 FY2026"},
  {"period": "2025-03-31", "label": "FY 2025"}  // Different format!
]
```

### 2. Use Section Headers

Break up long lists of metrics with section headers for readability:

```json
{"type": "section_header", "label": "REVENUE"},
{"type": "data", "label": "Sale of goods", "key": "sale_of_goods"},
{"type": "data", "label": "Export sales", "key": "export_sales"},
{"type": "total", "label": "Total Revenue", "key": "revenue_from_operations"},
{"type": "blank", "label": ""},
{"type": "section_header", "label": "EXPENSES"},
...
```

### 3. Blank Rows for Spacing

Use blank rows to visually separate sections:

```json
{"type": "total", "label": "Total Revenue", "key": "revenue_from_operations"},
{"type": "blank", "label": ""},
{"type": "section_header", "label": "EXPENSES"}
```

### 4. Meaningful Labels

Use clear, descriptive labels that match the financial statement terminology:

```json
{"type": "data", "label": "Revenue from operations", "key": "revenue_from_operations"}
// Better than:
{"type": "data", "label": "Rev Ops", "key": "revenue_from_operations"}
```

### 5. Key Matching

Ensure the `key` values match exactly what the AI extractor returns. Check the AI extraction JSON to see available keys:

```bash
# View extracted keys
cat output/BRITANNIA_*/Britannia_*-financial-data.json | jq 'keys'
```

## Troubleshooting

### Template Not Applied

**Symptom:** Excel still uses fixed 47-row format  
**Cause:** Template file not properly uploaded or invalid JSON  
**Solution:** Check template preview shows "X columns, Y rows" before generating

### Missing Data in Cells

**Symptom:** Cells show "-" instead of values  
**Cause:** Key mismatch between template and extracted data  
**Solution:**

1. Check extracted JSON: `output/COMPANY_*/filename-financial-data.json`
2. Verify template `key` values match JSON keys
3. Verify template `period` values match JSON date keys

### Invalid JSON Error

**Symptom:** "Invalid JSON in data field"  
**Cause:** Malformed JSON syntax  
**Solution:**

1. Validate JSON at https://jsonlint.com/
2. Check for missing commas, brackets, or quotes
3. Use a JSON editor with syntax highlighting

### Formatting Not Applied

**Symptom:** Section headers not bold/colored  
**Cause:** Type mismatch or formatting not defined  
**Solution:**

1. Ensure row `type` matches formatting key exactly
2. Define formatting for each type you use
3. Use valid hex color codes (6 characters, no #)

## API Response

When using a template, the API response includes:

```json
{
  "success": true,
  "message": "Excel file generated using AI and saved",
  "file_id": "abc123...",
  "used_template": true, // ← Indicates template was used
  "metadata": {
    "extraction_method": "ai",
    "model": "gpt-4o-mini"
  }
}
```

## Related Files

- **Default Template:** `excel_template_default.json` - Starting point template
- **AI Extractor:** `ai_extractor.py` - Extracts financial data using OpenAI
- **Excel Generator:** `excel_generator.py` - Generates Excel from template
- **Streamlit UI:** `streamlit_app.py` - AI Excel Generator tab
- **Flask API:** `app.py` - `/api/generate-excel-ai` endpoint

## Support

For issues or questions about JSON templates:

1. Check template JSON is valid at jsonlint.com
2. Review `excel_template_default.json` for correct structure
3. Verify extracted data keys in `output/` directory
4. Check Flask logs for detailed error messages

---

**Version:** 2.2.0  
**Last Updated:** 2025-01-15
