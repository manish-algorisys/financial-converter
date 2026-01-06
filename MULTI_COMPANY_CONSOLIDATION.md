# Multi-Company Consolidation Feature

## Overview

The multi-company consolidation feature allows users to compare financial data from multiple companies side-by-side in a single Excel file. This feature automatically detects companies from parsed documents and generates a consolidated view.

## Key Features

### 1. **Multi-Select UI**

- Select multiple parsed documents at once
- Automatic company name detection from folder structure
- Visual selection summary showing company breakdown

### 2. **Consolidated Excel Layout**

```
Column A: Metric (fixed)
Columns B-E: Company 1 (4 periods)
Column F: Blank separator
Columns G-J: Company 2 (4 periods)
Column K: Blank separator
Columns L-O: Company 3 (4 periods)
...and so on
```

### 3. **Intelligent Data Alignment**

- Automatically aligns metrics across companies
- Handles missing periods gracefully (shows '-' for unavailable data)
- Preserves formatting and styling

## How It Works

### Frontend (Streamlit UI)

**Location:** `streamlit_app.py` - Lines 1347-1570

**Changes:**

1. **Document Selection (Lines 1347-1400)**

   - Replaced single company/document dropdowns with multi-select
   - Scans `output/` folder for all `COMPANY_DocumentName` folders
   - Auto-extracts company name from folder structure
   - Shows selection summary and company breakdown

2. **Generate Button Logic (Lines 1500-1570)**

   - Detects single vs multi-company mode
   - Shows different UI for each mode
   - Calls appropriate API endpoint

3. **New Function (Lines 441-508)**
   ```python
   def generate_excel_ai_consolidated(documents, preferred_format='html',
                                     save_to_storage=False, template_excel_file=None)
   ```
   - Sends to `/api/generate-excel-ai-consolidated` endpoint
   - 300s timeout (vs 120s for single doc)
   - Returns consolidated Excel file

### Backend API

**Location:** `app.py` - New endpoint at line 1119

**New Endpoint:** `/api/generate-excel-ai-consolidated`

**Parameters:**

- `documents`: JSON array of `[{company, document}, ...]`
- `preferred_format`: 'html' or 'markdown'
- `save`: 'true' or 'false'
- `template_excel`: Optional Excel template file

**Process:**

1. Parse documents array from request
2. Loop through each document:
   - Find output directory
   - Extract data using AI
   - Collect financial_data
3. Call Excel generator with all companies' data
4. Return consolidated Excel file

### Excel Generation

**Location:** `excel_generator.py` - New method at line 1009

**New Method:** `generate_excel_consolidated(companies_data, output_path, template_excel_path=None)`

**Layout Algorithm:**

```python
# Calculate column offset for each company
col_offset = 1 + (company_index * 5)

# Company 1: Columns B-E (offset=1, positions 1-4)
# Blank: Column F (offset+4)
# Company 2: Columns G-J (offset=6, positions 6-9)
# Blank: Column K (offset+9)
# Company 3: Columns L-O (offset=11, positions 11-14)
```

**Features:**

- Row 1: Merged company names (e.g., B1:E1 = "BRITANNIA")
- Row 2: Period headers (e.g., "Q1 FY26", "Q2 FY26")
- Rows 3+: Metric data aligned across all companies
- Blank columns separate companies for visual clarity
- Standard formatting applied (bold headers, number formatting)

## Usage

### Via Streamlit UI

1. Navigate to "AI Excel Generator" tab
2. Select multiple parsed documents from the multi-select dropdown
3. (Optional) Upload an Excel template
4. Click "Generate Consolidated Excel using AI"
5. Review the consolidated Excel file

### Via API

```python
import requests
import json

# Prepare documents array
documents = [
    {'company': 'BRITANNIA', 'document': 'Britannia_Unaudited_Q2_June_2026'},
    {'company': 'HUL', 'document': 'HUL_Unaudited_Q2_June_2026'},
    {'company': 'NESTLE', 'document': 'Nestle_Unaudited_Q2_June_2026'}
]

# Call API
response = requests.post(
    'http://localhost:5000/api/generate-excel-ai-consolidated',
    data={
        'documents': json.dumps(documents),
        'preferred_format': 'html',
        'save': 'false'
    },
    timeout=300
)

# Save Excel file
if response.status_code == 200:
    with open('consolidated.xlsx', 'wb') as f:
        f.write(response.content)
```

### Test Script

Run `test_consolidation.py`:

```bash
python test_consolidation.py
```

This will:

- Scan for available parsed documents
- Select first 2 documents
- Generate consolidated Excel
- Open the file automatically (Windows)

## File Structure

```
d:\projects\docling_fin_parser\
├── app.py                      # Flask API (NEW endpoint added)
├── streamlit_app.py            # Streamlit UI (MODIFIED)
├── excel_generator.py          # Excel generation (NEW method added)
├── test_consolidation.py       # Test script (NEW)
└── output/
    ├── BRITANNIA_Britannia_Unaudited_Q2_June_2026/
    ├── HUL_HUL_Unaudited_Q2_June_2026/
    └── NESTLE_Nestle_Unaudited_Q2_June_2026/
```

## Technical Details

### Folder Naming Convention

The system expects parsed documents in folders following this pattern:

```
COMPANY_DocumentName
```

Example:

- `BRITANNIA_Britannia_Unaudited_Q2_June_2026`
- `ITC_ITC_Unaudited_Q2_June_2026`

The company name is extracted from the part before the first underscore.

### Period Alignment

The system:

1. Extracts all unique periods from all companies
2. Uses the first 4 periods (or all available if less than 4)
3. Fills '-' for companies missing specific periods

### Metric Standardization

Uses a standard list of 24 financial metrics:

- Revenue metrics (Sale of goods, Exports, Services, etc.)
- Expense metrics (Materials, Employee benefits, Depreciation, etc.)
- Profit metrics (PBT, PAT, EBITDA, etc.)
- Per-share metrics (EPS, etc.)

## Benefits

1. **Side-by-Side Comparison**: Compare multiple companies' performance in one view
2. **Time Savings**: No need to manually copy-paste data across files
3. **Consistency**: Metrics are automatically aligned across companies
4. **Flexibility**: Works with any number of companies (2+)
5. **Template Support**: Use custom Excel templates for branding/formatting

## Limitations

1. **Period Limitation**: Currently shows first 4 periods only
2. **Metric Standardization**: All companies must use same metric keys
3. **Memory**: Large number of companies may cause memory issues
4. **Processing Time**: Increases linearly with number of companies

## Future Enhancements

- [ ] Support for custom metric selection
- [ ] Period filtering/selection
- [ ] Comparison charts and visualizations
- [ ] Export to multiple formats (PDF, HTML)
- [ ] Ratio calculations across companies
- [ ] Year-over-year comparison mode

## Troubleshooting

### "No documents provided or invalid format"

- Ensure documents array is properly JSON-formatted
- Check that company and document fields are present

### "Output directory not found"

- Verify documents have been parsed first
- Check folder naming convention: `COMPANY_DocumentName`

### "No valid data extracted from any document"

- Check that HTML/Markdown files exist in output folders
- Verify AI extraction is working for individual documents

### Timeout errors

- Increase timeout in API call (default: 300s)
- Process fewer companies at once
- Check OpenAI API connectivity

## Version History

**v2.3.0 (Current)**

- Added multi-company consolidation feature
- Multi-select UI with auto-detection
- New API endpoint `/api/generate-excel-ai-consolidated`
- New Excel generation method `generate_excel_consolidated()`

## Support

For issues or questions:

1. Check console output for detailed error messages
2. Review Flask logs: `_log.error()` messages
3. Test with single company first to isolate issues
4. Verify all dependencies are installed: `pip install -r requirements.txt`
