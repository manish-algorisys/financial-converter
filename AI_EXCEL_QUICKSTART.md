# AI Excel Generator - Quick Start Guide

## Overview

The AI Excel Generator uses OpenAI's GPT models to extract financial data from previously parsed PDF documents and generate professional Excel statements. This decouples parsing from Excel generation, allowing you to:

1. **Parse once** - Extract tables from PDF to HTML/Markdown
2. **Generate multiple times** - Use AI to create Excel with different configurations
3. **Iterate quickly** - No need to re-upload and re-parse PDFs

---

## Prerequisites

### 1. Install Dependencies

```bash
pip install openai
# Or update all dependencies
pip install -r requirements.txt
```

### 2. Set OpenAI API Key

Create a `.env` file in the project root:

```bash
# .env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Or set as environment variable (Windows):

```bash
set OPENAI_API_KEY=sk-your-openai-api-key-here
```

Linux/Mac:

```bash
export OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3. Start the API Server

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Start Flask API
python app.py
```

The server should log: `"AI extractor initialized successfully"`

---

## Usage Workflows

### Workflow 1: Streamlit UI (Easiest)

1. **Start Streamlit:**

   ```bash
   streamlit run streamlit_app.py
   ```

2. **Parse a document** (Tab 1: Upload & Parse):

   - Upload PDF
   - Select company
   - Click "Parse Document"
   - Wait for parsing to complete

3. **Generate Excel with AI** (Tab 4: 🤖 AI Excel Generator):
   - Select the company
   - Choose the parsed document from dropdown
   - Click "🚀 Generate Excel with AI"
   - Download the generated file

### Workflow 2: API Endpoints

#### Step 1: Parse Document (if not already done)

```bash
curl -X POST http://localhost:5000/api/parse \
  -F "file=@sample-data/Britannia_Q2_June_2025.pdf" \
  -F "company_name=BRITANNIA"
```

This saves results to: `output/BRITANNIA_Britannia_Q2_June_2025/`

#### Step 2: Generate Excel with AI

```bash
curl -X POST http://localhost:5000/api/generate-excel-ai \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "BRITANNIA",
    "document_name": "Britannia_Q2_June_2025",
    "preferred_format": "html"
  }' \
  --output BRITANNIA_AI_Statement.xlsx
```

#### Step 3: Save to Storage (Optional)

```bash
curl -X POST http://localhost:5000/api/generate-excel-ai \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "BRITANNIA",
    "document_name": "Britannia_Q2_June_2025",
    "save": true
  }'
```

Response:

```json
{
  "success": true,
  "file_id": "abc123-def456-ghi789",
  "download_url": "/api/download-generated/abc123-def456-ghi789",
  "metadata": {
    "extraction_method": "openai",
    "model": "gpt-4o-mini",
    "tokens_used": 2450
  }
}
```

### Workflow 3: Python Script

```python
import requests

API_URL = "http://localhost:5000"

# Generate Excel with AI
response = requests.post(
    f"{API_URL}/api/generate-excel-ai",
    json={
        "company_name": "BRITANNIA",
        "document_name": "Britannia_Q2_June_2025",
        "preferred_format": "html",
        "save": False
    }
)

if response.status_code == 200:
    # Save file
    with open("output.xlsx", "wb") as f:
        f.write(response.content)
    print("✅ Excel generated successfully!")
else:
    error = response.json()
    print(f"❌ Error: {error.get('error')}")
```

---

## Configuration Options

### API Endpoint: POST /api/generate-excel-ai

**Request Body:**

```json
{
  "company_name": "BRITANNIA", // Required: Company name (uppercase)
  "document_name": "Britannia_Q2_2025", // Required: Output folder name (without company prefix)
  "preferred_format": "html", // Optional: "html" or "markdown" (default: "html")
  "save": false // Optional: Save to storage vs direct download
}
```

**Response (Direct Download):**

- Binary Excel file (`.xlsx`)
- Filename: `{COMPANY}_AI_financial_statement.xlsx`

**Response (Save to Storage):**

```json
{
  "success": true,
  "message": "Excel file generated using AI and saved",
  "file_id": "uuid-string",
  "download_url": "/api/download-generated/{file_id}",
  "metadata": {
    "extraction_method": "openai",
    "model": "gpt-4o-mini",
    "tokens_used": 2450,
    "source_format": "html"
  }
}
```

---

## Cost Optimization

### Token Usage

- **Average per extraction:** 2000-5000 tokens
- **Cost (GPT-4o-mini):** ~$0.001-$0.003 per extraction
- **Model options:** `gpt-4o-mini` (default, cheaper) or `gpt-4o` (more accurate)

### Tips to Reduce Costs

1. **Use HTML format** (more structured than Markdown)
2. **Cache results** (generate once, download multiple times with `save=true`)
3. **Batch processing** (future enhancement)
4. **Use gpt-4o-mini** for standard reports (default)
5. **Monitor token usage** via metadata in response

---

## Troubleshooting

### Error: "AI extraction not available"

**Cause:** OPENAI_API_KEY not set or invalid

**Solution:**

```bash
# Check if key is set
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows

# Set the key
export OPENAI_API_KEY=sk-...  # Linux/Mac
set OPENAI_API_KEY=sk-...     # Windows

# Restart Flask API
python app.py
```

### Error: "No parsed results found"

**Cause:** Document not parsed yet or incorrect document_name

**Solution:**

1. Check output folder exists: `output/{COMPANY}_{DOCUMENT_NAME}/`
2. Parse document first using `/api/parse`
3. Verify document_name matches folder name (without company prefix)

**Example:**

- Folder: `output/BRITANNIA_Britannia_Q2_June_2025/`
- document*name should be: `"Britannia_Q2_June_2025"` (NOT including "BRITANNIA*")

### Error: "No suitable table files found"

**Cause:** HTML/MD files not generated during parsing

**Solution:**

1. Re-parse the document
2. Check `output/{COMPANY}_{DOC}/` contains `*-table-*.html` or `*-table-*.md` files
3. If missing, parsing may have failed - check logs

### Error: "Invalid JSON response from OpenAI"

**Cause:** AI model returned malformed JSON or content was truncated

**Solution:**

1. Try with `preferred_format: "html"` (more structured)
2. Check HTML file size - very large files get truncated
3. Review logs for raw OpenAI response
4. Consider using `gpt-4o` for complex documents (more robust)

### High Token Usage

**Cause:** Large HTML files or complex tables

**Solution:**

1. Current limit: 30,000 chars (~7500 tokens)
2. Extracts only table content, not full HTML
3. If still too large, consider:
   - Pre-processing HTML to extract <table> only
   - Using Markdown format (more compact)
   - Splitting very large reports

---

## Advanced Usage

### Custom AI Model

Modify `ai_extractor.py`:

```python
# Initialize with different model
ai_extractor = AIFinancialExtractor(
    api_key="sk-...",
    model="gpt-4o"  # More accurate but costlier
)
```

### Batch Processing Multiple Documents

```python
import requests

API_URL = "http://localhost:5000"

documents = [
    {"company": "BRITANNIA", "doc": "Britannia_Q2_2025"},
    {"company": "COLGATE", "doc": "Colgate_Q2_2025"},
    {"company": "DABUR", "doc": "Dabur_Q2_2025"}
]

for doc in documents:
    response = requests.post(
        f"{API_URL}/api/generate-excel-ai",
        json={
            "company_name": doc["company"],
            "document_name": doc["doc"],
            "save": True
        }
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ {doc['company']}: {result['file_id']}")
    else:
        print(f"❌ {doc['company']}: Failed")
```

### Validating Extracted Data

```python
from ai_extractor import validate_financial_data

# After extraction
extracted_data = ai_extractor.extract_from_html(html_path, "BRITANNIA")

# Validate structure
try:
    validate_financial_data(extracted_data)
    print("✅ Data structure is valid")
except ValueError as e:
    print(f"❌ Validation error: {e}")
```

---

## Comparison: Config vs AI Extraction

| Feature                | Config-Driven                     | AI-Powered                   |
| ---------------------- | --------------------------------- | ---------------------------- |
| **Speed**              | Fast (1-2s)                       | Slower (30-60s)              |
| **Accuracy**           | High (if format matches)          | High (adapts to variations)  |
| **Setup**              | Requires config mapping           | Zero setup                   |
| **Cost**               | Free                              | ~$0.001-$0.003 per doc       |
| **Format Flexibility** | Low (needs exact format)          | High (handles variations)    |
| **Best For**           | Standard reports, bulk processing | One-off reports, prototyping |

**Recommendation:** Use config-driven for production, AI for edge cases and prototyping.

---

## Next Steps

1. **Review AI_PROMPTS.md** for advanced prompt engineering
2. **Check copilot-instructions.md** for architecture details
3. **Explore Streamlit UI** for interactive experience
4. **Monitor token usage** to optimize costs

---

## Support

For issues or questions:

- Check logs in terminal
- Review [AI_PROMPTS.md](AI_PROMPTS.md) for debugging prompts
- Inspect intermediate HTML files in `output/` directory
- Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`

---

**Last Updated:** December 22, 2025
