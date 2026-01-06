# Debugging Multi-Company Consolidation

## Common Errors and Solutions

### Error: "Expecting value: line 1 column 1 (char 0)"

**Cause:** JSON parsing error - usually means:

1. API response is empty
2. Trying to parse non-JSON content
3. Missing parameters in API call

**Fixed Issues:**

- ✅ `extract_from_output_dir()` missing `company_name` parameter
- ✅ Streamlit sending JSON instead of form data when no template
- ✅ Inconsistent request format between template/no-template cases

**Solutions Applied:**

1. Added `company_name` parameter to `extract_from_output_dir()` call
2. Changed Streamlit to always send form data (not JSON)
3. Improved error handling with try-catch blocks
4. Added detailed logging for debugging

### Error: "No valid data extracted from any document"

**Possible Causes:**

1. Documents haven't been parsed yet
2. Output folder structure incorrect
3. AI extraction failing
4. Missing HTML/Markdown files

**Check:**

```python
# Verify folder structure
output/
├── COMPANY_DocumentName/
│   ├── DocumentName-table-1.html
│   ├── DocumentName-table-1.md
│   └── DocumentName-financial-data.json
```

**Debug Steps:**

1. Check Flask logs for detailed error messages
2. Verify OPENAI_API_KEY is set in .env
3. Test single company extraction first
4. Check if HTML/MD files exist in output folders

### Error: "Cannot connect to AI API"

**Solutions:**

1. Ensure Flask server is running: `python app.py`
2. Check API_URL in streamlit_app.py (default: http://localhost:5000)
3. Verify no firewall blocking localhost connections

## Debugging Workflow

### Step 1: Check Parsed Documents

```bash
ls output/
```

Should show folders like:

- `BRITANNIA_Britannia_Unaudited_Q2_June_2026`
- `ITC_ITC_Unaudited_Q2_June_2026`
- `HUL_HUL_Unaudited_Q2_June_2026`

### Step 2: Verify AI Extraction Works for Single Company

Test with single company first:

```python
# In Streamlit, select ONE document
# Click "Generate Excel using AI"
# Should work without errors
```

### Step 3: Check Flask Logs

Enable debug logging in app.py:

```python
logging.basicConfig(level=logging.DEBUG)
```

Look for:

- "Extracted data for COMPANY/DOCUMENT" (success)
- "Error extracting data for COMPANY/DOCUMENT" (failure)
- "Total companies with extracted data: N"

### Step 4: Test API Endpoint Directly

```python
import requests
import json

documents = [
    {'company': 'BRITANNIA', 'document': 'Britannia_Unaudited_Q2_June_2026'},
    {'company': 'ITC', 'document': 'ITC_Unaudited_Q2_June_2026'}
]

response = requests.post(
    'http://localhost:5000/api/generate-excel-ai-consolidated',
    data={
        'documents': json.dumps(documents),
        'preferred_format': 'html',
        'save': 'false'
    },
    timeout=300
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"File size: {len(response.content)} bytes")
else:
    print(f"Error: {response.json()}")
```

### Step 5: Check Environment

```bash
# Check Python environment
python --version  # Should be 3.8+

# Check required packages
pip list | grep -E "openpyxl|openai|requests|fuzzywuzzy"

# Check environment variables
cat .env | grep OPENAI_API_KEY
```

## Key Changes Made

### app.py (Lines 1191-1211)

**Before:**

```python
extracted_data = extractor.extract_from_output_dir(output_dir, source_format)
```

**After:**

```python
extracted_data = extractor.extract_from_output_dir(output_dir, company_name, source_format)
```

**Reason:** Missing required `company_name` parameter

### streamlit_app.py (Lines 446-478)

**Before:**

```python
else:
    # Regular JSON request
    payload = {
        'documents': documents,
        'preferred_format': preferred_format,
        'save': save_to_storage
    }
    response = requests.post(
        f"{API_URL}/api/generate-excel-ai-consolidated",
        json=payload,
        timeout=300
    )
```

**After:**

```python
else:
    # Regular form data request (no files)
    response = requests.post(
        f"{API_URL}/api/generate-excel-ai-consolidated",
        data=data,
        timeout=300
    )
```

**Reason:** Backend expects form data with JSON-stringified documents, not JSON body

## Testing After Fix

### Quick Test

```bash
# 1. Start Flask
python app.py

# 2. Start Streamlit (new terminal)
streamlit run streamlit_app.py

# 3. In Streamlit:
#    - Go to "AI Excel Generator" tab
#    - Select 2+ documents
#    - Click "Generate Consolidated Excel"
```

### Expected Output

- Processing message
- Excel file download (if save=false)
- Success message with company names

### Success Indicators

- No JSON parsing errors
- Companies data extracted: 2+ companies
- Excel file generated successfully
- File size > 10 KB (not empty)

## Still Having Issues?

1. **Enable verbose logging:**

   ```python
   # Add to app.py after imports
   import logging
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   ```

2. **Check AI extractor directly:**

   ```python
   from ai_extractor import AIFinancialExtractor
   from pathlib import Path

   extractor = AIFinancialExtractor()
   output_dir = Path("output/BRITANNIA_Britannia_Unaudited_Q2_June_2026")
   result = extractor.extract_from_output_dir(output_dir, "BRITANNIA", "html")
   print(result)
   ```

3. **Verify Excel generation:**

   ```python
   from excel_generator import FinancialExcelGenerator
   from pathlib import Path

   generator = FinancialExcelGenerator()
   companies_data = [...]  # Your extracted data
   output_path = Path("test_consolidated.xlsx")
   success = generator.generate_excel_consolidated(companies_data, output_path)
   print(f"Success: {success}")
   ```

## Contact & Support

If issues persist:

1. Check Flask terminal for full stack traces
2. Check Streamlit terminal for frontend errors
3. Review OPENAI_API_KEY is valid and has credits
4. Ensure all dependencies updated: `pip install -r requirements.txt --upgrade`
