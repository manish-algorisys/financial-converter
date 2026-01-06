# Batch Processing API Documentation

## Overview

The Financial Document Parser API now supports **automatic company name detection** and **batch processing** capabilities. This allows you to:

1. **Auto-detect company names** from PDF content (no manual input needed)
2. **Process multiple PDFs** in a single request
3. **Scan and process entire folders** of PDFs

---

## New Features (v2.3)

### ✨ Auto-Detection

- Company names are automatically detected from PDF content
- Supports all 7 companies: BRITANNIA, COLGATE, DABUR, HUL, ITC, NESTLE, P&G
- Scans first 3 pages for company name patterns
- Fallback to manual specification if detection fails

### 📦 Batch Processing

- Upload multiple PDFs in single API call
- Each file auto-detects its company name independently
- Returns aggregated results with success/failure statistics

### 📁 Folder Processing

- Process all PDFs in a specified folder
- Recursive scanning for PDF files
- Automatic company detection for each file

---

## API Endpoints

### 1. Single File Parsing (Enhanced with Auto-Detection)

**Endpoint:** `POST /api/parse`

**Changes:**

- `company_name` parameter is now **OPTIONAL**
- If not provided, company name is auto-detected from PDF
- Returns `detected_company` field when auto-detection is used

**Request (with auto-detection):**

```bash
curl -X POST http://localhost:5000/api/parse \
  -F "file=@Britannia_Q2_2025.pdf" \
  -F "prefer_standalone=true" \
  -F "use_fuzzy_matching=true"
# Note: No company_name parameter
```

**Request (manual override):**

```bash
curl -X POST http://localhost:5000/api/parse \
  -F "file=@Britannia_Q2_2025.pdf" \
  -F "company_name=BRITANNIA" \
  -F "prefer_standalone=true" \
  -F "use_fuzzy_matching=true"
```

**Response (auto-detected):**

```json
{
  "success": true,
  "message": "Successfully processed document...",
  "detected_company": "BRITANNIA",
  "data": {
    "company_name": "BRITANNIA",
    "financial_data": [...]
  },
  "output_files": {...},
  "processing_time": 45.2,
  "table_info": {...}
}
```

**Python Example:**

```python
import requests

with open('Britannia_Q2.pdf', 'rb') as f:
    files = {'file': f}
    data = {
        'prefer_standalone': 'true',
        'use_fuzzy_matching': 'true'
        # No company_name - will auto-detect
    }

    response = requests.post('http://localhost:5000/api/parse',
                            files=files, data=data)

    result = response.json()
    print(f"Detected: {result['detected_company']}")
```

---

### 2. Batch Processing (Multiple Files)

**Endpoint:** `POST /api/parse-batch`

**Description:** Upload multiple PDF files and process them all in one request. Each file's company name is auto-detected independently.

**Form Data Parameters:**

- `files[]`: Multiple PDF files (required, array)
- `prefer_standalone`: Prefer standalone statements (optional, default: true)
- `use_fuzzy_matching`: Enable fuzzy matching (optional, default: true)

**Request:**

```bash
curl -X POST http://localhost:5000/api/parse-batch \
  -F "files[]=@Britannia_Q2.pdf" \
  -F "files[]=@ITC_Q2.pdf" \
  -F "files[]=@HUL_Q2.pdf" \
  -F "prefer_standalone=true" \
  -F "use_fuzzy_matching=true"
```

**Response:**

```json
{
  "success": true,
  "message": "Batch processing completed",
  "summary": {
    "total": 3,
    "successful": 2,
    "failed": 1
  },
  "results": [
    {
      "filename": "Britannia_Q2.pdf",
      "success": true,
      "detected_company": "BRITANNIA",
      "message": "Successfully processed document",
      "data": {...},
      "output_files": {...},
      "processing_time": 42.5,
      "table_info": {...}
    },
    {
      "filename": "ITC_Q2.pdf",
      "success": true,
      "detected_company": "ITC",
      "message": "Successfully processed document",
      "data": {...},
      "output_files": {...},
      "processing_time": 38.1,
      "table_info": {...}
    },
    {
      "filename": "Unknown_Q2.pdf",
      "success": false,
      "error": "Could not auto-detect company name"
    }
  ]
}
```

**Python Example:**

```python
import requests
from pathlib import Path

pdf_files = [
    'Britannia_Q2.pdf',
    'ITC_Q2.pdf',
    'HUL_Q2.pdf'
]

files = []
for pdf_path in pdf_files:
    files.append(('files[]', (Path(pdf_path).name, open(pdf_path, 'rb'))))

data = {
    'prefer_standalone': 'true',
    'use_fuzzy_matching': 'true'
}

response = requests.post('http://localhost:5000/api/parse-batch',
                        files=files, data=data)

# Close file handles
for _, (_, f) in files:
    f.close()

result = response.json()
print(f"Total: {result['summary']['total']}")
print(f"Successful: {result['summary']['successful']}")
print(f"Failed: {result['summary']['failed']}")

for file_result in result['results']:
    status = "✅" if file_result['success'] else "❌"
    print(f"{status} {file_result['filename']} - {file_result.get('detected_company', 'N/A')}")
```

---

### 3. Folder Processing

**Endpoint:** `POST /api/parse-folder`

**Description:** Process all PDF files in a specified folder. The API scans the folder for PDFs and auto-detects company names for each.

**JSON Body Parameters:**

- `folder_path`: Absolute path to folder containing PDFs (required)
- `prefer_standalone`: Prefer standalone statements (optional, default: true)
- `use_fuzzy_matching`: Enable fuzzy matching (optional, default: true)

**Request:**

```bash
curl -X POST http://localhost:5000/api/parse-folder \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "/path/to/financial_reports/Q2_2025",
    "prefer_standalone": true,
    "use_fuzzy_matching": true
  }'
```

**Windows Example:**

```bash
curl -X POST http://localhost:5000/api/parse-folder \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "D:/reports/Q2_2025",
    "prefer_standalone": true,
    "use_fuzzy_matching": true
  }'
```

**Response:**

```json
{
  "success": true,
  "message": "Folder processing completed",
  "summary": {
    "total": 5,
    "successful": 4,
    "failed": 1
  },
  "results": [
    {
      "filename": "Britannia_Q2_June_2025.pdf",
      "success": true,
      "detected_company": "BRITANNIA",
      "message": "Successfully processed document",
      "data": {...},
      "output_files": {...},
      "processing_time": 45.3,
      "table_info": {...}
    },
    {
      "filename": "ITC_Results_Q2.pdf",
      "success": true,
      "detected_company": "ITC",
      "message": "Successfully processed document",
      "data": {...},
      "output_files": {...},
      "processing_time": 39.7,
      "table_info": {...}
    },
    {
      "filename": "unknown_report.pdf",
      "success": false,
      "error": "Could not auto-detect company name"
    }
  ]
}
```

**Python Example:**

```python
import requests

payload = {
    "folder_path": "D:/financial_reports/Q2_2025",
    "prefer_standalone": True,
    "use_fuzzy_matching": True
}

response = requests.post(
    'http://localhost:5000/api/parse-folder',
    json=payload,
    headers={'Content-Type': 'application/json'}
)

result = response.json()

if result['success']:
    print(f"Processed {result['summary']['total']} files")
    print(f"✅ Successful: {result['summary']['successful']}")
    print(f"❌ Failed: {result['summary']['failed']}")

    for file_result in result['results']:
        if file_result['success']:
            print(f"\n{file_result['filename']}:")
            print(f"  Company: {file_result['detected_company']}")
            print(f"  Items: {len(file_result['data']['financial_data'])}")
            print(f"  Time: {file_result['processing_time']:.2f}s")
        else:
            print(f"\n❌ {file_result['filename']}: {file_result['error']}")
```

---

## Company Detection Patterns

The API detects companies using regex patterns:

| Company       | Detection Patterns                               |
| ------------- | ------------------------------------------------ |
| **BRITANNIA** | britannia, britannia industries                  |
| **COLGATE**   | colgate, colgate-palmolive, colgate palmolive    |
| **DABUR**     | dabur, dabur india                               |
| **HUL**       | hindustan unilever, hul, unilever                |
| **ITC**       | itc, itc limited, i.t.c                          |
| **NESTLE**    | nestle, nestlé, nestle india                     |
| **P&G**       | procter & gamble, procter and gamble, p&g, p & g |

**Detection Method:**

1. Extracts text from first 3 pages of PDF
2. Searches for company-specific patterns (case-insensitive)
3. Returns first match found
4. Returns `None` if no patterns match

---

## Error Handling

### Single File Errors

**Auto-detection failed:**

```json
{
  "success": false,
  "error": "Could not auto-detect company name. Please provide company_name parameter."
}
```

**Invalid company name:**

```json
{
  "success": false,
  "error": "Unsupported company: XYZ. Supported: ['BRITANNIA', 'COLGATE', ...]"
}
```

### Batch Processing Errors

Individual file failures are included in `results` array:

```json
{
  "filename": "problematic_file.pdf",
  "success": false,
  "error": "Could not auto-detect company name"
}
```

### Folder Processing Errors

**Folder not found:**

```json
{
  "success": false,
  "error": "Folder does not exist: /invalid/path"
}
```

**No PDFs found:**

```json
{
  "success": false,
  "error": "No PDF files found in: /empty/folder"
}
```

---

## Best Practices

### 1. Auto-Detection vs Manual

✅ **Use Auto-Detection When:**

- Processing PDFs with standard company headers
- Batch processing multiple companies
- Quick prototyping/testing

⚠️ **Use Manual Override When:**

- Company name detection fails
- Custom/modified PDF formats
- Specific company must be enforced

### 2. Batch Processing

✅ **Recommended:**

```python
# Process 5-10 files per batch for optimal performance
files = ['file1.pdf', 'file2.pdf', 'file3.pdf']  # ✅ Good
```

⚠️ **Avoid:**

```python
# Processing 50+ files in single request (timeout risk)
files = [f'file{i}.pdf' for i in range(100)]  # ❌ Too many
```

**Alternative:** Use folder processing endpoint for large batches

### 3. Folder Processing

✅ **Recommended:**

- Organize PDFs by quarter/period in folders
- Use absolute paths (avoid relative paths)
- Ensure proper file permissions

```
D:/reports/
  ├── Q1_2025/
  │   ├── Britannia_Q1.pdf
  │   └── ITC_Q1.pdf
  ├── Q2_2025/
  │   ├── Britannia_Q2.pdf
  │   └── ITC_Q2.pdf
```

### 4. Error Recovery

Check `summary` field in batch/folder responses:

```python
result = response.json()
if result['summary']['failed'] > 0:
    # Handle failures
    for file_result in result['results']:
        if not file_result['success']:
            print(f"Failed: {file_result['filename']}")
            print(f"Reason: {file_result['error']}")
            # Retry with manual company_name or investigate PDF
```

---

## Performance Considerations

### Processing Times

| Operation         | Avg Time | Files |
| ----------------- | -------- | ----- |
| Single File       | 40-50s   | 1     |
| Batch (5 files)   | 200-250s | 5     |
| Folder (10 files) | 400-500s | 10    |

**Factors affecting performance:**

- PDF complexity (pages, tables)
- OCR requirements
- Table structure accuracy mode
- System resources (CPU, RAM)

### Recommendations

1. **Use batch/folder endpoints** instead of multiple single requests
2. **Set reasonable timeouts** (60-120s per file)
3. **Monitor memory usage** for large batches
4. **Process files in parallel** using multiple API instances (if needed)

---

## Migration Guide

### From v2.2 to v2.3

**Old Code (manual company name):**

```python
with open('britannia.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/parse',
        files={'file': f},
        data={'company_name': 'BRITANNIA'}  # Manual
    )
```

**New Code (auto-detection):**

```python
with open('britannia.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/parse',
        files={'file': f}
        # company_name auto-detected
    )

result = response.json()
print(f"Detected: {result.get('detected_company')}")
```

**Backward Compatible:**

- Old code still works (manual company_name honored)
- New field `detected_company` added to response
- No breaking changes to existing endpoints

---

## Testing

Run the included test script:

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Run tests
python api_batch_examples.py
```

**Test Suite Includes:**

1. Single file with auto-detection
2. Single file with manual override
3. Batch processing (3 files)
4. Folder processing (all sample PDFs)

---

## Troubleshooting

### Issue: "Could not auto-detect company name"

**Causes:**

- Company name not in first 3 pages
- Non-standard PDF format
- Scanned/image-based PDF without OCR text

**Solutions:**

1. Manually specify `company_name` parameter
2. Check PDF has extractable text
3. Review company name patterns (case-insensitive)

### Issue: Batch processing timeout

**Solutions:**

1. Reduce batch size (5-10 files recommended)
2. Increase client timeout settings
3. Use folder processing endpoint
4. Process files in multiple batches

### Issue: Folder path not found (Windows)

**Common Mistake:**

```json
{ "folder_path": "D:\reportsQ2" } // ❌ Backslash escaping issue
```

**Solution:**

```json
{"folder_path": "D:/reports/Q2"}  // ✅ Forward slashes
{"folder_path": "D:\\reports\\Q2"}  // ✅ Escaped backslashes
```

---

## API Reference Summary

| Endpoint            | Method | Auto-Detect | Batch | Description             |
| ------------------- | ------ | ----------- | ----- | ----------------------- |
| `/api/parse`        | POST   | ✅          | ❌    | Single file (enhanced)  |
| `/api/parse-batch`  | POST   | ✅          | ✅    | Multiple files upload   |
| `/api/parse-folder` | POST   | ✅          | ✅    | Folder-based processing |

**All endpoints support:**

- ✅ Auto company name detection
- ✅ `prefer_standalone` option
- ✅ `use_fuzzy_matching` option
- ✅ Detailed error reporting
- ✅ Processing time metrics

---

## Support

For issues or questions:

1. Check this documentation
2. Review `api_batch_examples.py` for code examples
3. Check Flask server logs for detailed errors
4. Verify PDF format and company name patterns
