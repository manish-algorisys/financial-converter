# Excel/CSV Generation API Documentation

Complete API reference for generating professional financial statements in Excel and CSV formats.

## Table of Contents

- [Overview](#overview)
- [Extraction Modes](#extraction-modes)
- [API Endpoints](#api-endpoints)
- [Workflows](#workflows)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

The Excel/CSV generation API provides two powerful ways to create professional financial statements from PDF documents:

### Features

- **47-Row Financial Statement**: Standardized format covering revenue, expenses, PBT, tax, and profit metrics
- **Professional Styling**: Bold headers, gray backgrounds, borders, and double underlines
- **Indian Number Formatting**: Lakhs/crores style with comma separators (12,34,567)
- **Bracket Negatives**: `(123)` represents -123 (accounting standard)
- **Dynamic Periods**: Auto-detects 4-24 periods from source data
- **Multiple Formats**: Excel (.xlsx) and CSV outputs
- **File Management**: UUID-based storage with metadata tracking

### Output Structure

```
Financial Statement (47 rows × dynamic columns)
├── Particulars (Column A)
├── Period columns (Columns B-L, auto-detected)
│   ├── Jun 2025, Mar 2025, Jun 2024, etc.
│   └── Empty columns if fewer periods available
└── Sections:
    ├── Revenue from Operations (Rows 1-10)
    ├── Expenses (Rows 11-25)
    ├── PBT & Tax (Rows 26-32)
    ├── Net Profit (Rows 33-36)
    ├── EBITDA (Rows 37-40)
    └── Growth Metrics (Rows 41-47)
```

## Extraction Modes

### Mode 1: Config-Driven Extraction

**Pros:**

- ✅ **Fast**: No AI API calls, instant processing
- ✅ **Free**: No additional costs
- ✅ **Accurate**: Uses pre-configured row mappings from config.json
- ✅ **Predictable**: Consistent results for supported companies

**Cons:**

- ⚠️ **Limited**: Only works for companies in config.json
- ⚠️ **Maintenance**: Requires config updates for format changes

**When to Use:**

- Supported companies (Britannia, Colgate, Dabur, HUL, ITC, Nestlé, P&G)
- Regular quarterly reports with consistent formats
- High-volume processing where cost matters
- Production systems requiring predictable behavior

### Mode 2: AI-Powered Extraction

**Pros:**

- ✅ **Universal**: Works with ANY financial report format
- ✅ **Zero-Config**: No need to update config.json
- ✅ **Smart**: Automatically detects all metrics and periods
- ✅ **Adaptive**: Handles format variations gracefully

**Cons:**

- 💰 **Cost**: ~$0.001-$0.003 per document (GPT-4o-mini)
- ⏱️ **Slower**: 2-5 seconds for AI processing
- 🔑 **Requires API Key**: OPENAI_API_KEY must be set

**When to Use:**

- New companies not in config.json
- One-off custom financial reports
- PDF format variations not covered by config
- Prototyping and testing new sources

## API Endpoints

### 1. Parse PDF (Prerequisite for Both Modes)

**Endpoint**: `POST /api/parse`

Extracts tables from PDF and saves HTML/Markdown for later use.

**Request**:

```bash
curl -X POST http://localhost:5000/api/parse \
  -F "file=@financial_report.pdf" \
  -F "company_name=BRITANNIA"
```

**Response**:

```json
{
  "success": true,
  "message": "Successfully parsed financial data",
  "data": {
    "financial_data": {
      "30.06.2025": { "sale_of_goods": 4357.64, ... },
      "31.03.2025": { "sale_of_goods": 4512.30, ... },
      "30.06.2024": { "sale_of_goods": 3891.45, ... },
      "31.03.2025_Y": { "sale_of_goods": 17234.78, ... }
    },
    "metadata": {
      "source_file": "Britannia_Unaudited_Q2_June_2026.pdf",
      "extraction_method": "tr_number",
      "processing_time": 12.45
    }
  }
}
```

**Saved Files** (in `output/{COMPANY}_{DOCUMENT_NAME}/`):

- `{document_name}-table-1.html` - HTML table for AI extraction
- `{document_name}-table-1.md` - Markdown table for AI extraction
- `{document_name}-financial-data.json` - Extracted JSON data

---

### 2. Generate Excel (Config-Driven)

**Endpoint**: `POST /api/generate-excel`

Generates Excel from JSON data (from `/api/parse` response).

**Request**:

```bash
curl -X POST http://localhost:5000/api/generate-excel \
  -H "Content-Type: application/json" \
  -d '{
    "financial_data": {
      "30.06.2025": { "sale_of_goods": 4357.64, ... },
      "31.03.2025": { "sale_of_goods": 4512.30, ... }
    }
  }' \
  --output statement.xlsx
```

**Request with Save**:

```bash
curl -X POST http://localhost:5000/api/generate-excel \
  -H "Content-Type: application/json" \
  -d '{
    "financial_data": { ... },
    "save": true,
    "metadata": {
      "company": "BRITANNIA",
      "document_type": "quarterly_results",
      "source_file": "Q2_2025.pdf"
    }
  }'
```

**Response (save=false)**: Binary Excel file (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)

**Response (save=true)**:

```json
{
  "success": true,
  "message": "Excel file generated and saved successfully",
  "file_id": "abc123-def456-ghi789",
  "download_url": "/api/download-generated/abc123-def456-ghi789",
  "metadata": {
    "company": "BRITANNIA",
    "file_type": "excel",
    "created_at": "2025-12-26T10:30:00"
  }
}
```

---

### 3. Generate Excel (AI-Powered) 🤖

**Endpoint**: `POST /api/generate-excel-ai`

Generates Excel using AI extraction from previously saved HTML/Markdown.

**Request**:

```bash
curl -X POST http://localhost:5000/api/generate-excel-ai \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "BRITANNIA",
    "document_name": "Britannia_Unaudited_Q2_June_2026",
    "preferred_format": "html"
  }' \
  --output statement.xlsx
```

**Request with Save**:

```bash
curl -X POST http://localhost:5000/api/generate-excel-ai \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "NEWCOMPANY",
    "document_name": "NEWCOMPANY_Q1_2025",
    "preferred_format": "html",
    "save": true
  }'
```

**Parameters**:

- `company_name` (required): Company identifier (uppercase)
- `document_name` (required): Document name from parse step (without extension)
- `preferred_format` (optional): `"html"` or `"markdown"` (default: `"html"`)
- `save` (optional): Save to storage (default: `false`)

**Response (save=false)**: Binary Excel file

**Response (save=true)**:

```json
{
  "success": true,
  "message": "Excel file generated with AI extraction",
  "file_id": "xyz789-abc123-def456",
  "download_url": "/api/download-generated/xyz789-abc123-def456",
  "metadata": {
    "extraction_method": "openai",
    "model": "gpt-4o-mini",
    "tokens_used": 3500,
    "cost_estimate_usd": 0.00175,
    "processing_time": 3.2
  }
}
```

**Headers in Response**:

- `X-Extraction-Method`: "openai"
- `X-Model`: "gpt-4o-mini"
- `X-Tokens-Used`: "3500"
- `X-Processing-Time`: "3.2"

---

### 4. Generate CSV

**Endpoint**: `POST /api/generate-csv`

Generates CSV file from JSON data.

**Request**:

```bash
curl -X POST http://localhost:5000/api/generate-csv \
  -H "Content-Type: application/json" \
  -d @financial_data.json \
  --output statement.csv
```

**Response**: CSV file with same structure as Excel (plain text)

---

### 5. List Generated Files

**Endpoint**: `GET /api/list-generated-files`

Lists all generated Excel/CSV files with metadata.

**Request**:

```bash
curl http://localhost:5000/api/list-generated-files
```

**Optional Query Parameters**:

- `company`: Filter by company name
- `file_type`: Filter by file type (`excel` or `csv`)

**Response**:

```json
{
  "success": true,
  "files": [
    {
      "file_id": "abc123-def456",
      "company": "BRITANNIA",
      "file_type": "excel",
      "created_at": "2025-12-26T10:30:00",
      "download_count": 3,
      "size_bytes": 45678,
      "download_url": "/api/download-generated/abc123-def456"
    }
  ],
  "total_files": 12
}
```

---

### 6. Download Generated File

**Endpoint**: `GET /api/download-generated/<file_id>`

Downloads a previously generated Excel/CSV file.

**Request**:

```bash
curl http://localhost:5000/api/download-generated/abc123-def456 \
  --output statement.xlsx
```

**Response**: Binary file download with appropriate Content-Type

---

### 7. Delete Generated File

**Endpoint**: `DELETE /api/delete-generated/<file_id>`

Deletes a generated file from storage.

**Request**:

```bash
curl -X DELETE http://localhost:5000/api/delete-generated/abc123-def456
```

**Response**:

```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

## Workflows

### Workflow 1: Config-Driven (Traditional)

**Best for**: Supported companies, high-volume processing, cost-sensitive applications

```bash
# Step 1: Parse PDF
curl -X POST http://localhost:5000/api/parse \
  -F "file=@britannia_q2.pdf" \
  -F "company_name=BRITANNIA" \
  > parse_result.json

# Step 2: Extract financial_data from response
# (Use jq or manually extract the financial_data object)

# Step 3: Generate Excel directly
curl -X POST http://localhost:5000/api/generate-excel \
  -H "Content-Type: application/json" \
  -d @financial_data.json \
  --output statement.xlsx
```

**Python Example**:

```python
import requests

# Step 1: Parse PDF
with open('britannia_q2.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/parse',
        files={'file': f},
        data={'company_name': 'BRITANNIA'}
    )

parse_result = response.json()
financial_data = parse_result['data']['financial_data']

# Step 2: Generate Excel
response = requests.post(
    'http://localhost:5000/api/generate-excel',
    json={'financial_data': financial_data}
)

# Step 3: Save Excel
with open('statement.xlsx', 'wb') as f:
    f.write(response.content)

print("Excel generated successfully!")
```

---

### Workflow 2: AI-Powered (Zero-Config)

**Best for**: New companies, one-off reports, format variations, prototyping

```bash
# Step 1: Parse PDF (saves HTML/MD files)
curl -X POST http://localhost:5000/api/parse \
  -F "file=@newcompany_report.pdf" \
  -F "company_name=NEWCOMPANY" \
  > parse_result.json

# Step 2: Extract document_name from response
# document_name will be like "NEWCOMPANY_newcompany_report"

# Step 3: Generate Excel with AI
curl -X POST http://localhost:5000/api/generate-excel-ai \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "NEWCOMPANY",
    "document_name": "NEWCOMPANY_newcompany_report"
  }' \
  --output statement.xlsx
```

**Python Example**:

```python
import requests

# Step 1: Parse PDF
with open('newcompany_report.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/parse',
        files={'file': f},
        data={'company_name': 'NEWCOMPANY'}
    )

parse_result = response.json()
source_file = parse_result['data']['metadata']['source_file']
document_name = f"NEWCOMPANY_{source_file.replace('.pdf', '')}"

# Step 2: Generate Excel with AI
response = requests.post(
    'http://localhost:5000/api/generate-excel-ai',
    json={
        'company_name': 'NEWCOMPANY',
        'document_name': document_name,
        'preferred_format': 'html'
    }
)

# Step 3: Save Excel
with open('statement.xlsx', 'wb') as f:
    f.write(response.content)

# Step 4: Check AI metadata
tokens_used = response.headers.get('X-Tokens-Used', 'N/A')
model = response.headers.get('X-Model', 'N/A')
print(f"Generated with {model}, Tokens: {tokens_used}")
```

---

### Workflow 3: Batch Processing

**Process multiple PDFs and save to storage**

```python
import requests
import os
from pathlib import Path

def batch_process_pdfs(pdf_directory, company_name, use_ai=False):
    """Process all PDFs in directory and generate Excel files"""

    results = []

    for pdf_file in Path(pdf_directory).glob('*.pdf'):
        print(f"Processing {pdf_file.name}...")

        # Step 1: Parse PDF
        with open(pdf_file, 'rb') as f:
            response = requests.post(
                'http://localhost:5000/api/parse',
                files={'file': f},
                data={'company_name': company_name}
            )

        if not response.json()['success']:
            print(f"Failed to parse {pdf_file.name}")
            continue

        parse_result = response.json()
        source_file = parse_result['data']['metadata']['source_file']
        document_name = f"{company_name}_{source_file.replace('.pdf', '')}"

        # Step 2: Generate Excel
        if use_ai:
            # AI-powered extraction
            response = requests.post(
                'http://localhost:5000/api/generate-excel-ai',
                json={
                    'company_name': company_name,
                    'document_name': document_name,
                    'save': True
                }
            )
        else:
            # Config-driven extraction
            financial_data = parse_result['data']['financial_data']
            response = requests.post(
                'http://localhost:5000/api/generate-excel',
                json={
                    'financial_data': financial_data,
                    'save': True,
                    'metadata': {
                        'company': company_name,
                        'source_file': pdf_file.name
                    }
                }
            )

        if response.json()['success']:
            result = response.json()
            results.append({
                'file': pdf_file.name,
                'file_id': result['file_id'],
                'download_url': result['download_url']
            })
            print(f"✓ Generated Excel: {result['file_id']}")
        else:
            print(f"✗ Failed to generate Excel for {pdf_file.name}")

    return results

# Usage
results = batch_process_pdfs(
    pdf_directory='./quarterly_reports',
    company_name='BRITANNIA',
    use_ai=False
)

print(f"\nProcessed {len(results)} files successfully")
```

## Error Handling

### Common Errors

#### 1. Missing HTML/Markdown Files

**Error**:

```json
{
  "success": false,
  "error": "Neither HTML nor Markdown file found. Run /api/parse first."
}
```

**Solution**: Always run `/api/parse` before `/api/generate-excel-ai`

#### 2. Missing OPENAI_API_KEY

**Error**:

```json
{
  "success": false,
  "error": "OPENAI_API_KEY environment variable not set"
}
```

**Solution**: Set API key in `.env` file:

```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

#### 3. Invalid JSON Structure

**Error**:

```json
{
  "success": false,
  "error": "Missing required field: financial_data"
}
```

**Solution**: Ensure JSON includes `financial_data` object with period keys

#### 4. File Not Found

**Error**:

```json
{
  "success": false,
  "error": "File not found: abc123"
}
```

**Solution**: Verify file_id exists using `/api/list-generated-files`

#### 5. AI Extraction Failed

**Error**:

```json
{
  "success": false,
  "error": "AI extraction failed: Invalid API response"
}
```

**Solutions**:

- Check OPENAI_API_KEY validity
- Verify internet connection
- Check OpenAI service status
- Try fallback to markdown format: `"preferred_format": "markdown"`

### Error Response Format

All errors follow this structure:

```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "details": {
    // Optional, for debugging
    "field": "field_name",
    "expected": "expected_value",
    "received": "actual_value"
  }
}
```

## Best Practices

### 1. Choose the Right Extraction Mode

```
Is company in config.json?
├─ YES → Use config-driven (/api/generate-excel)
│         ✓ Faster, free, more accurate
└─ NO  → Use AI-powered (/api/generate-excel-ai)
          ✓ Works with any format, zero config
```

### 2. Optimize AI Costs

- **Reuse Parsed Files**: Run `/api/parse` once, generate Excel multiple times
- **Use HTML Format**: Slightly better structure than Markdown for tables
- **Batch Processing**: Process multiple PDFs in sequence to amortize startup costs
- **Monitor Usage**: Track `X-Tokens-Used` header to estimate costs

### 3. File Management

- **Save Important Files**: Use `save=true` for files you need later
- **Regular Cleanup**: Delete old files to save storage
- **Download Counts**: Track `download_count` to identify popular reports
- **Metadata Tags**: Use metadata to organize files by quarter, year, type

### 4. Error Handling

```python
import requests
import time

def generate_excel_with_retry(data, max_retries=3):
    """Generate Excel with automatic retry on failure"""

    for attempt in range(max_retries):
        try:
            response = requests.post(
                'http://localhost:5000/api/generate-excel',
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                return response.content

            # Log error and retry
            print(f"Attempt {attempt + 1} failed: {response.status_code}")
            time.sleep(2 ** attempt)  # Exponential backoff

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)

    raise Exception("Failed to generate Excel after retries")
```

### 5. Validation

```python
def validate_financial_data(data):
    """Validate financial data structure before Excel generation"""

    # Check required top-level key
    if 'financial_data' not in data:
        raise ValueError("Missing 'financial_data' key")

    financial_data = data['financial_data']

    # Check has at least one period
    if not financial_data:
        raise ValueError("financial_data is empty")

    # Check each period has data
    for period, metrics in financial_data.items():
        if not isinstance(metrics, dict):
            raise ValueError(f"Period {period} must be a dict")

        if not metrics:
            raise ValueError(f"Period {period} has no metrics")

    return True
```

### 6. Performance Monitoring

```python
import time

def monitor_excel_generation(data):
    """Monitor Excel generation performance"""

    start_time = time.time()

    response = requests.post(
        'http://localhost:5000/api/generate-excel',
        json=data
    )

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"Generation time: {elapsed:.2f}s")
    print(f"File size: {len(response.content) / 1024:.2f} KB")

    # Check for AI usage
    if 'X-Tokens-Used' in response.headers:
        tokens = response.headers['X-Tokens-Used']
        model = response.headers['X-Model']
        print(f"AI used: {model}, Tokens: {tokens}")

    return response.content
```

## Examples

### Example 1: Simple Excel Generation

```python
import requests

# Prepare data
data = {
    "financial_data": {
        "30.06.2025": {
            "sale_of_goods": 4357.64,
            "other_operating_revenues": 123.45,
            "total_revenue": 4481.09
        },
        "31.03.2025": {
            "sale_of_goods": 4512.30,
            "other_operating_revenues": 145.67,
            "total_revenue": 4657.97
        }
    }
}

# Generate Excel
response = requests.post(
    'http://localhost:5000/api/generate-excel',
    json=data
)

# Save file
with open('statement.xlsx', 'wb') as f:
    f.write(response.content)
```

### Example 2: AI Extraction with Error Handling

```python
import requests
import sys

def generate_with_ai(company_name, document_name):
    """Generate Excel using AI with comprehensive error handling"""

    try:
        # Attempt AI extraction
        response = requests.post(
            'http://localhost:5000/api/generate-excel-ai',
            json={
                'company_name': company_name,
                'document_name': document_name,
                'preferred_format': 'html'
            },
            timeout=60
        )

        if response.status_code == 200:
            # Success - save file
            filename = f"{company_name}_statement.xlsx"
            with open(filename, 'wb') as f:
                f.write(response.content)

            # Log usage
            tokens = response.headers.get('X-Tokens-Used', 'N/A')
            print(f"✓ Generated {filename}")
            print(f"  Tokens used: {tokens}")
            return filename

        else:
            # API error
            error_data = response.json()
            print(f"✗ API Error: {error_data.get('error')}")
            return None

    except requests.exceptions.Timeout:
        print("✗ Request timed out (>60s)")
        return None

    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API server")
        return None

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None

# Usage
result = generate_with_ai('NEWCOMPANY', 'NEWCOMPANY_Q1_2025')
if result:
    print(f"Saved to: {result}")
else:
    sys.exit(1)
```

### Example 3: Compare Config vs AI Extraction

```python
import requests
import time

def compare_extraction_methods(pdf_file, company_name):
    """Compare config-driven vs AI-powered extraction"""

    # Step 1: Parse PDF (saves both HTML and JSON)
    with open(pdf_file, 'rb') as f:
        parse_response = requests.post(
            'http://localhost:5000/api/parse',
            files={'file': f},
            data={'company_name': company_name}
        )

    parse_result = parse_response.json()
    financial_data = parse_result['data']['financial_data']
    source_file = parse_result['data']['metadata']['source_file']
    document_name = f"{company_name}_{source_file.replace('.pdf', '')}"

    results = {}

    # Method 1: Config-driven
    start = time.time()
    config_response = requests.post(
        'http://localhost:5000/api/generate-excel',
        json={'financial_data': financial_data}
    )
    config_time = time.time() - start

    results['config_driven'] = {
        'time': config_time,
        'size': len(config_response.content),
        'cost': 0,
        'file': 'config_statement.xlsx'
    }

    with open('config_statement.xlsx', 'wb') as f:
        f.write(config_response.content)

    # Method 2: AI-powered
    start = time.time()
    ai_response = requests.post(
        'http://localhost:5000/api/generate-excel-ai',
        json={
            'company_name': company_name,
            'document_name': document_name
        }
    )
    ai_time = time.time() - start

    tokens_used = int(ai_response.headers.get('X-Tokens-Used', 0))
    cost_estimate = (tokens_used / 1_000_000) * 0.15  # GPT-4o-mini pricing

    results['ai_powered'] = {
        'time': ai_time,
        'size': len(ai_response.content),
        'cost': cost_estimate,
        'tokens': tokens_used,
        'file': 'ai_statement.xlsx'
    }

    with open('ai_statement.xlsx', 'wb') as f:
        f.write(ai_response.content)

    # Print comparison
    print("Extraction Method Comparison")
    print("=" * 50)
    print(f"Config-Driven:")
    print(f"  Time: {results['config_driven']['time']:.2f}s")
    print(f"  Size: {results['config_driven']['size'] / 1024:.2f} KB")
    print(f"  Cost: $0.00 (free)")
    print()
    print(f"AI-Powered:")
    print(f"  Time: {results['ai_powered']['time']:.2f}s")
    print(f"  Size: {results['ai_powered']['size'] / 1024:.2f} KB")
    print(f"  Cost: ${results['ai_powered']['cost']:.5f}")
    print(f"  Tokens: {results['ai_powered']['tokens']:,}")

    return results

# Usage
compare_extraction_methods('britannia_q2.pdf', 'BRITANNIA')
```

## Rate Limits & Quotas

### OpenAI API Limits

- **GPT-4o-mini**: 30,000 tokens/minute (default tier)
- **Typical Document**: 3,000-5,000 tokens
- **Max Documents/Minute**: ~6-10 documents

### File Storage Limits

- **Max File Size**: 50 MB per PDF
- **Storage Directory**: `excel_storage/`
- **Metadata**: `excel_storage/metadata.json`
- **Cleanup**: Manual deletion via API

## Support & Resources

- **Quick Start**: [EXCEL_QUICKSTART.md](EXCEL_QUICKSTART.md)
- **AI Quick Start**: [AI_EXCEL_QUICKSTART.md](AI_EXCEL_QUICKSTART.md)
- **Environment Setup**: [SETUP_ENV.md](SETUP_ENV.md)
- **Implementation**: [EXCEL_IMPLEMENTATION_SUMMARY.md](EXCEL_IMPLEMENTATION_SUMMARY.md)
- **Main README**: [README.md](README.md)

## Changelog

### v2.2 (December 2025)

- ✨ Added AI-powered extraction via `/api/generate-excel-ai`
- 📊 Support for dynamic period detection (4-24 columns)
- 🔄 Decoupled parsing from Excel generation
- 💰 Cost tracking with token usage headers

### v2.1 (November 2025)

- 📊 Initial Excel/CSV generation
- 💾 File storage with UUID management
- 🎨 Professional styling and formatting
- 📁 File management endpoints

---

**Last Updated**: December 26, 2025  
**Version**: 2.2  
**License**: MIT
