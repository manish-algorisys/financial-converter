# JSON Template Feature - Implementation Summary

## Overview

Implemented JSON-based template system for AI Excel Generator tab, allowing users to define custom Excel structures instead of using the fixed 47-row format.

## What Was Changed

### 1. Created Default Template (`excel_template_default.json`)

- **11 columns** (periods from Q1 FY2026 back to FY 2023)
- **47 rows** (matching original fixed format structure)
- Row types: section_header, data, total, metric, blank
- Formatting specifications for different row types
- Layout configuration (title row, header row, data start)

### 2. Updated AI Extractor (`ai_extractor.py`)

**Line ~23:** Modified `SYSTEM_PROMPT`

- Added explanation of template structure
- Clarified: "Column A contains particulars (metric names), Row 1 contains periods (dates)"
- Ensures AI understands output format requirements

### 3. Enhanced Excel Generator (`excel_generator.py`)

**Lines 1-5:** Updated docstring

- Mentions template support

**Lines 19-23:** Updated class docstring

- Documents two modes: fixed format vs JSON template-based

**Lines 213-226:** Modified `generate_excel()` signature

- Added `template_json_path=None` parameter
- Checks if template exists, calls `_generate_from_json_template()` if provided

**Lines 336-475:** NEW METHOD `_generate_from_json_template()`

- Loads JSON template file
- Creates Excel workbook dynamically
- Title row with company name (merged cells)
- Period headers in Row 2 from columns array
- Data rows from rows specification
- Type-based formatting:
  - `section_header`: Bold + gray background
  - `total`: Bold + light background
  - `metric`: Bold
  - `data`: Standard formatting
  - `blank`: Empty row
- Fills data using existing `_get_value()` method
- Applies borders to all cells
- Returns success boolean

### 4. Updated Streamlit UI (`streamlit_app.py`)

**Lines 377-441:** Modified `generate_excel_ai()` function

- Added `template_json_file` parameter
- Handles multipart requests when template provided
- Sends template as 'template_json' file in multipart form-data
- Includes template in request body if uploaded

**Lines 1395-1458:** NEW JSON Template Upload Section

- Expander: "Custom Excel Template (JSON Format)"
- Documentation of template structure within UI
- File uploader for JSON templates (accepts .json files)
- Template preview showing:
  - Number of columns defined
  - Number of rows defined
  - First 3 columns (period + label)
  - First 3 rows (type + label + key)
- Stores uploaded template in session state

**Lines 1488-1495:** Updated Generate Button Handler

- Retrieves template from `st.session_state.get('ai_json_template_uploader')`
- Passes template file to `generate_excel_ai()` function

### 5. Updated Flask API (`app.py`)

**Line 5:** Added `import json`

**Lines 931-1010:** Modified `/api/generate-excel-ai` endpoint

- Accepts both JSON and multipart/form-data requests
- Extracts 'template_json' file from multipart request
- Saves template to temporary location using `secure_filename()`
- Passes `template_json_path` to `generator.generate_excel()`
- Cleans up temporary template file after generation
- Returns `used_template: true` in response when template provided
- Error handling for invalid JSON in multipart data field
- Cleanup on errors and after file download

**Lines 1020-1050:** Updated Excel Generation Logic

- Checks if template_temp_path exists
- Calls `generate_excel(extracted_data, excel_file, template_json_path=template_temp_path)`
- Falls back to fixed format if no template provided
- Logs template usage for debugging

## How It Works

### Template Structure

```json
{
  "columns": [
    {
      "period": "30.06.2025",
      "label": "Q1 FY2026",
      "description": "3M-30th Jun 2025"
    }
  ],
  "rows": [
    { "type": "section_header", "label": "REVENUE", "key": "" },
    { "type": "data", "label": "Sale of goods", "key": "sale_of_goods" }
  ],
  "formatting": {
    "section_header": { "bold": true, "background_color": "D3D3D3" }
  },
  "layout": {
    "title_row": 1,
    "period_header_row": 2,
    "data_start_row": 3
  }
}
```

### User Workflow

1. **Upload PDF** → Parse → AI Extract
2. **Navigate to AI Excel Generator** tab
3. **Expand "Custom Excel Template"** section
4. **Upload JSON template** (optional - uses default if not provided)
5. **Review preview** (shows X columns, Y rows)
6. **Click Generate Excel**
7. **Download** custom-structured Excel file

### API Workflow

```
Client → POST /api/generate-excel-ai (multipart)
       ↓
     Flask API extracts:
       - data (JSON string)
       - template_json (file)
       ↓
     Saves template to temp location
       ↓
     AI Extractor reads HTML/Markdown
       ↓
     Excel Generator:
       - Loads JSON template
       - Creates dynamic Excel structure
       - Fills data cells
       - Applies formatting
       ↓
     Returns Excel file
       ↓
     Cleans up temp files
```

### Data Matching

For each data cell:

1. Row `key` (e.g., "sale_of_goods") matches extracted data key
2. Column `period` (e.g., "30.06.2025") matches date key
3. Cell value = `extracted_data[row.key][column.period]`
4. Formatted using `_format_number()` (Indian notation with brackets for negatives)

## File Locations

### New Files

- `excel_template_default.json` - Default template specification
- `JSON_TEMPLATE_GUIDE.md` - Comprehensive user guide

### Modified Files

- `ai_extractor.py` - Updated prompt for template awareness
- `excel_generator.py` - Added template-based generation method
- `streamlit_app.py` - Added template upload UI
- `app.py` - Updated API endpoint for multipart requests

## Testing Checklist

- [ ] Upload JSON template in Streamlit UI
- [ ] Verify template preview shows correct column/row count
- [ ] Generate Excel with template
- [ ] Verify Excel structure matches template
- [ ] Check Column A has correct particulars
- [ ] Check Row 1 has correct periods
- [ ] Verify data cells filled correctly
- [ ] Test formatting (bold, backgrounds) applied
- [ ] Test with no template (fallback to fixed format)
- [ ] Test API endpoint with multipart request
- [ ] Verify `used_template: true` in API response
- [ ] Test template cleanup (no orphaned temp files)

## Key Features

✅ **Flexible Structure** - Define any number of rows and columns  
✅ **Type-Based Formatting** - Different styles for headers, totals, metrics  
✅ **Template Preview** - See structure before generating  
✅ **Backward Compatible** - Works without template (uses fixed format)  
✅ **AI Aware** - Prompt updated to understand template structure  
✅ **Clean API** - Handles both JSON and multipart requests  
✅ **Secure** - Uses `secure_filename()` for template uploads  
✅ **Cleanup** - Automatic temp file removal

## Implementation Statistics

- **Files Created:** 2 (excel_template_default.json, JSON_TEMPLATE_GUIDE.md)
- **Files Modified:** 4 (ai_extractor.py, excel_generator.py, streamlit_app.py, app.py)
- **Lines Added:** ~250
- **New Method:** `_generate_from_json_template()` (140 lines)
- **API Changes:** Multipart support in `/api/generate-excel-ai`

## Benefits Over Fixed Format

| Aspect        | Fixed Format          | JSON Template                    |
| ------------- | --------------------- | -------------------------------- |
| Row Count     | 47 (hardcoded)        | Any (configurable)               |
| Columns       | 11 periods (fixed)    | Any periods (configurable)       |
| Structure     | P&L only              | Any structure                    |
| Customization | Code changes required | JSON edit only                   |
| Use Cases     | Standard reports      | Custom reports, KPIs, dashboards |
| Maintenance   | Code updates          | Config updates                   |

## Next Steps (Optional Enhancements)

1. **Template Library** - Create folder with sample templates (quarterly, annual, KPI, etc.)
2. **Template Validation** - Add JSON schema validation before generation
3. **Template Builder UI** - Visual template editor in Streamlit
4. **Conditional Formatting** - Add rules for value-based formatting (e.g., color negatives red)
5. **Calculated Fields** - Support formulas in template (e.g., "Total = A + B")
6. **Multi-Sheet Support** - Generate workbooks with multiple sheets from template
7. **Export Templates** - Allow saving current structure as template
8. **Template Versioning** - Track template changes over time

## Documentation

- **User Guide:** `JSON_TEMPLATE_GUIDE.md` - Complete reference
- **Default Template:** `excel_template_default.json` - Working example
- **AI Instructions:** `.github/copilot-instructions.md` - Updated architecture notes

---

**Implementation Date:** 2025-01-15  
**Version:** 2.2.0  
**Status:** ✅ Complete - Ready for testing
