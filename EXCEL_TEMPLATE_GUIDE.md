# Excel Template Feature - User Guide

## Overview

The AI Excel Generator now supports **custom Excel templates**. Instead of using a fixed 47-row format or JSON configuration, you can upload your own Excel file with placeholders that will be automatically filled with AI-extracted financial data.

## How It Works

1. **Create an Excel template** with your desired layout
2. **Add placeholders** using `{{key[period]}}` syntax where you want data filled
3. **Upload the template** in the AI Excel Generator tab
4. **Generate Excel** - placeholders will be replaced with extracted data

⚠️ **Important:** If you upload a template without any placeholders, it will be returned as-is without data filling. Make sure to add at least one placeholder like `{{company_name}}` or `{{revenue_from_operations[30.06.2025]}}` to have data populated.

## Placeholder Syntax

### Basic Format

```
{{key[period]}}
```

### Examples

| Placeholder                               | Description           | Example Output               |
| ----------------------------------------- | --------------------- | ---------------------------- |
| `{{company_name}}`                        | Company name          | BRITANNIA INDUSTRIES LIMITED |
| `{{revenue_from_operations[30.06.2025]}}` | Revenue for Q1 FY2026 | 4,357.64                     |
| `{{net_profit[31.03.2025_Y]}}`            | Net profit for FY2025 | 1,234.56                     |
| `{{eps_basic[30.06.2024]}}`               | EPS for Q1 FY2025     | 45.67                        |

## Available Keys

### Revenue Section

- `sale_of_goods`
- `export_sales`
- `service_revenue`
- `other_operating_revenues`
- `revenue_from_operations`
- `other_income`
- `total_income`

### Expense Section

- `cost_of_materials_consumed`
- `excise_duty`
- `purchases_stock_in_trade`
- `changes_in_inventories`
- `employee_benefits_expense`
- `finance_costs`
- `depreciation_amortisation_expense`
- `other_expense`
- `advertising_expense`
- `impairment_losses`
- `total_expenses`

### Profit & Tax Section

- `profit_before_exceptional_and_tax`
- `exceptional_item_expense`
- `profit_before_tax`
- `current_tax`
- `deferred_tax`
- `total_tax_expense`
- `net_profit`

### Other Comprehensive Income

- `oci_non_reclass_items`
- `tax_on_non_reclass_items`
- `other_comprehensive_income`
- `total_comprehensive_income`

### Equity & EPS

- `paid_up_equity_share_capital`
- `other_equity`
- `eps_basic`
- `eps_diluted`

## Period Formats

### Quarterly Periods

Use format: `DD.MM.YYYY`

- `30.06.2025` - Q1 FY2026 (June 30, 2025)
- `30.09.2024` - Q2 FY2025 (September 30, 2024)
- `31.12.2024` - Q3 FY2025 (December 31, 2024)
- `31.03.2025` - Q4 FY2025 (March 31, 2025)

### Yearly/Annual Periods

Use format: `DD.MM.YYYY_Y` (append `_Y` suffix)

- `31.03.2025_Y` - Full year FY2025
- `31.03.2024_Y` - Full year FY2024

## Sample Template

A sample template is available at: `templates/financial_summary_template.xlsx`

### Template Structure

```
┌─────────────────────────────────────────────────────┐
│     Financial Summary Report                        │
│     Company: {{company_name}}                       │
├─────────────────┬──────────┬──────────┬─────────────┤
│ Metric          │ Q1 FY2026│ Q1 FY2025│ FY2025      │
├─────────────────┼──────────┼──────────┼─────────────┤
│ Revenue from Ops│ {{rev[Q1]│ {{rev[Q1]│ {{rev[FY]}} │
│ Other Income    │ {{oi[Q1]}│ {{oi[Q1]}│ {{oi[FY]}}  │
│ Total Income    │ {{ti[Q1]}│ {{ti[Q1]}│ {{ti[FY]}}  │
│                 │          │          │             │
│ Total Expenses  │ {{te[Q1]}│ {{te[Q1]}│ {{te[FY]}}  │
│ Profit Before Tax│{{pbt[Q1]}│{{pbt[Q1]}│{{pbt[FY]}} │
│ Net Profit      │ {{np[Q1]}│ {{np[Q1]}│ {{np[FY]}}  │
└─────────────────┴──────────┴──────────┴─────────────┘
```

## Creating Your Template

### Step 1: Design Layout in Excel

1. Open Excel and create your desired layout
2. Add headers, formatting, charts, etc.
3. Merge cells, apply colors, borders as needed

### Step 2: Add Placeholders

Replace data cells with placeholders:

**Example:**

```excel
A1: Financial Dashboard
A2: Company: {{company_name}}
A4: Revenue
B4: {{revenue_from_operations[30.06.2025]}}
C4: {{revenue_from_operations[30.06.2024]}}
```

### Step 3: Save Template

Save as `.xlsx` or `.xls` file

### Step 4: Upload & Generate

1. Go to **AI Excel Generator** tab
2. Expand **"📋 Custom Excel Template"**
3. Upload your template file
4. Click **"🚀 Generate Excel with AI"**

## Number Formatting

Numbers will be formatted automatically:

- **Commas:** `1,234.56`
- **Negatives:** `(123.45)` or `-123.45`
- **Empty/Zero:** `-`
- **Decimals:** 2 decimal places by default

## Advanced Features

### Multiple Sheets

Templates can have multiple sheets - all sheets will be processed.

### Formulas

You can include Excel formulas that reference placeholder cells:

```excel
A1: Revenue: {{revenue_from_operations[30.06.2025]}}
A2: Expenses: {{total_expenses[30.06.2025]}}
A3: =A1-A2  (This formula will calculate based on filled values)
```

### Conditional Formatting

Excel's conditional formatting will work on filled values:

```
If cell > 0 → Green
If cell < 0 → Red
```

### Charts

Charts referencing template ranges will update automatically after filling.

## Troubleshooting

### Placeholder Not Replaced

**Issue:** Placeholder shows as `{{key[period]}}` in output

**Solutions:**

- Check key spelling (see Available Keys section)
- Verify period format (DD.MM.YYYY or DD.MM.YYYY_Y)
- Ensure data was extracted for that period
- Check for typos in curly braces

### No Placeholders Found

**Issue:** Uploaded template but got back the same file without data

**Reason:** Template doesn't contain any placeholders - system returned it unchanged

**Solution:**

- Add placeholders to your template using `{{key[period]}}` syntax
- Example: Replace cell value "Revenue" with `{{revenue_from_operations[30.06.2025]}}`
- At minimum, add `{{company_name}}` somewhere in your template

### Error Message in Cell

**Issue:** Cell shows `{{ERROR: key needs period}}`

**Solution:** Add period to placeholder: `{{key[30.06.2025]}}`

### Number Shows as Text

**Issue:** Number doesn't calculate in formulas

**Solution:** Template will try to convert to numbers automatically. If issues persist, remove quotes/special characters from placeholder.

### Missing Data

**Issue:** Cell shows `-` instead of value

**Reason:** Data not available for that key/period combination in extracted results

**Check:**

- View AI extraction results
- Verify PDF contains that metric
- Try different source format (HTML vs Markdown)

## Best Practices

✅ **Do:**

- Use descriptive headers
- Apply formatting before adding placeholders
- Test with sample data first
- Keep placeholder syntax exact
- Use consistent period formats

❌ **Don't:**

- Modify placeholder syntax (must be exactly `{{key[period]}}`)
- Use unsupported keys (see Available Keys)
- Mix period formats (use either DD.MM.YYYY or DD.MM.YYYY_Y)
- Add spaces inside curly braces

## Example Use Cases

### 1. Executive Dashboard

```excel
┌─────────────────────────────────────────┐
│ {{company_name}} - Executive Summary   │
├─────────────┬──────────┬───────────────┤
│ KPI         │ Current  │ YoY Growth %  │
├─────────────┼──────────┼───────────────┤
│ Revenue     │ {{rev}}  │ =(B2-C2)/C2   │
│ Profit      │ {{np}}   │ =(B3-C3)/C3   │
│ EPS         │ {{eps}}  │ =(B4-C4)/C4   │
└─────────────┴──────────┴───────────────┘
```

### 2. Quarterly Comparison

```excel
Q1 | Q2 | Q3 | Q4
{{metric[30.06.2025]}} | {{metric[30.09.2024]}} | ...
```

### 3. Multi-Year Analysis

```excel
FY2025 | FY2024 | FY2023
{{metric[31.03.2025_Y]}} | {{metric[31.03.2024_Y]}} | {{metric[31.03.2023_Y]}}
```

### 4. Custom P&L Format

```excel
Revenue:           {{revenue_from_operations[30.06.2025]}}
  - Cost of Sales: {{cost_of_materials_consumed[30.06.2025]}}
  = Gross Profit:  =B1-B2

Operating Exp:     {{other_expense[30.06.2025]}}
  = EBIT:          =B3-B4
```

## API Usage

If using the API directly:

```bash
curl -X POST http://localhost:5000/api/generate-excel-ai \
  -F "company_name=BRITANNIA" \
  -F "document_name=Britannia_Unaudited_Q2_June_2026" \
  -F "preferred_format=html" \
  -F "save=false" \
  -F "template_excel=@templates/financial_summary_template.xlsx"
```

## Version History

- **v2.3** - Excel template support with placeholder syntax
- **v2.2** - JSON template support (deprecated in favor of Excel)
- **v2.1** - AI-powered extraction
- **v2.0** - Fixed 47-row format

---

**Need Help?** Check the main README.md or contact support.
