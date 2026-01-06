# Financial Document Parser - AI Agent Instructions

## Architecture Overview

This is a **PDF-to-JSON financial data extraction system** with dual interfaces (Flask REST API + Streamlit UI). The core flow: `PDF → Docling (table extraction) → BeautifulSoup (HTML parsing) → config-driven extraction → JSON/Excel/CSV output`.

**Key Components:**

- [parser_core.py](parser_core.py): Core extraction logic - page detection, table parsing, fuzzy matching
- [app.py](app.py): Flask REST API with 12+ endpoints for parsing, editing, and file generation
- [streamlit_app.py](streamlit_app.py): Web UI with 5-tab interface for upload/review/AI/results/files
- [excel_generator.py](excel_generator.py): Generates styled 47-row Excel/CSV financial statements
- [ai_extractor.py](ai_extractor.py): **NEW** - AI-powered extraction using OpenAI GPT models
- [config.json](config.json): **Company-specific parsing rules** - column layouts, row mappings, labels

## Critical Patterns & Conventions

### 1. Config-Driven Extraction (config.json)

All company parsing rules live in [config.json](config.json). Each company has:

- `column_layout`: Maps dates to table column indices (e.g., `"30.06.2025": 3`)
- `financial_data[]`: Array of metrics with `key`, `labels[]`, and `tr_number` (1-indexed row number)

**Example:**

```json
{
  "britannia": {
    "column_layout": "standard",
    "financial_data": [
      { "key": "sale_of_goods", "labels": ["Sale of goods"], "tr_number": 5 }
    ]
  }
}
```

**When adding new companies:** Update both config.json AND the `company_mapping` dict in [parser_core.py](parser_core.py#L105-L113).

### 2. Dual Extraction Strategy (tr_number + Fuzzy Matching)

[parser_core.py](parser_core.py#L164-L180) uses TWO methods:

1. **Primary:** `tr_number` (fast, if PDF format matches config)
2. **Fallback:** Fuzzy label matching via `_find_matching_row()` (handles format variations)

Track extraction method in `result["extraction_method"]` - can be `"tr_number"`, `"mixed"`, or `"fuzzy"`.

### 3. Smart Page Detection with Priorities

[find_target_page()](parser_core.py#L35-L74) uses tiered regex matching:

1. **Priority 1:** Explicit "standalone" mentions
2. **Priority 2:** Generic patterns WITHOUT "consolidated" keyword
3. **Priority 3:** Fallback to any financial results page

**Never hardcode dates in regex** - patterns must work across any quarter/year.

### 4. Intelligent Table Selection

When multiple tables detected, [\_select_best_table()](parser_core.py#L231-L272) scores them:

```python
score = (min(rows, 50) × 2) + (financial_keywords × 10) + (has_numbers × 20) - (small_penalty × 30)
```

Selects table with highest score. Document selection method in `table_info["selection_method"]`.

### 5. Indian Number Formatting

[excel_generator.py](excel_generator.py#L68-L87) uses special formatting:

- **Negatives:** Bracket notation `(123)` not `-123`
- **Commas:** Indian style (lakhs/crores) - `12,34,567`
- **Empty values:** Display as `-` not `0.00`

### 6. UUID-Based File Management

[FileManager class](excel_generator.py#L200-L350) stores generated Excel/CSV files with:

- UUID filenames (security - no path traversal)
- Metadata JSON tracking company, type, download counts
- Auto-cleanup of orphaned files

### 7. AI-Powered Extraction (NEW - v2.2)

[ai_extractor.py](ai_extractor.py) provides OpenAI-based extraction:

- **Alternative to config-driven parsing** - uses GPT models to extract data from HTML/Markdown
- **System prompt** defines strict JSON structure with financial metrics ([see line 27](ai_extractor.py#L27))
- **Smart source selection** - tries HTML first, falls back to Markdown
- **Token optimization** - truncates content to ~7500 tokens max
- **Validation** - enforces schema via `validate_financial_data()`

**When to use AI extraction:**

- PDF format differs significantly from config expectations
- Quick prototyping for new companies
- Handling one-off custom reports
- Fuzzy matching fails repeatedly

**Workflow:** `/api/parse` → saves HTML/MD → `/api/generate-excel-ai` → reads HTML/MD → OpenAI extraction → Excel

## Developer Workflows

### Running the Application

```bash
# Activate venv first (Windows)
venv\Scripts\activate

# Terminal 1: Start Flask API (port 5000)
python app.py

# Terminal 2: Start Streamlit UI (port 8501)
streamlit run streamlit_app.py
```

**Testing:** Use [api_examples.py](api_examples.py) for quick API testing.

### Adding a New Company

1. Add column layout to `config.json` if needed (or reuse `"standard"`)
2. Add company config with all 30+ financial metrics
3. Update `company_mapping` dict in [parser_core.py](parser_core.py#L105)
4. Update `get_supported_companies()` return list in [parser_core.py](parser_core.py#L487)
5. Test with sample PDF using `/api/parse` endpoint

### Debugging Extraction Issues

1. Check `extraction_method` in JSON response - if `"fuzzy"`, row numbers don't match
2. Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`
3. Inspect intermediate HTML files in `output/` directory
4. Use `table_info` metadata to see which table was selected

### Key Configuration Files

- `.env`: API keys, environment vars (DO NOT commit) - **Required:** `OPENAI_API_KEY` for AI extraction
- [config.json](config.json): Parsing rules (1000+ lines)
- [requirements.txt](requirements.txt): Python dependencies - includes Docling, EasyOCR, OpenAI

## API Response Patterns

All endpoints return consistent structure:

```json
{
  "success": true/false,
  "message": "Human-readable status",
  "data": {},          // Main payload
  "error": "..."       // If success=false
}
```

Parse endpoint includes metadata:

```json
{
  "table_info": {
    "total_tables": 3,
    "selected_table": 1,
    "selection_method": "heuristic"
  },
  "processing_time": 45.2,
  "metadata": { "extraction_method": "tr_number" }
}
```

## Important Constraints

- **File size limit:** 50MB (set in [app.py](app.py#L37))
- **Supported formats:** PDF only (validated in [allowed_file()](app.py#L59))
- **Excel rows:** Fixed 47-row structure - do NOT modify without updating Excel templates
- **Date keys:** Use `_Y` suffix for yearly periods (e.g., `"31.03.2025_Y"`)
- **Company names:** MUST be uppercase in API requests

## References

- **AI Prompts Guide:** [AI_PROMPTS.md](AI_PROMPTS.md) - reusable prompts for code generation, testing, enhancements
- **PDF Optimization Guide:** [PDF_OPTIMIZATION.md](PDF_OPTIMIZATION.md) - details on fuzzy matching, page detection
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md) - setup instructions
- **Visual Guide:** [VISUAL_GUIDE.md](VISUAL_GUIDE.md) - UI screenshots and workflows

## Common Pitfalls

❌ **Don't** hardcode date patterns in regex (breaks for different quarters)  
✅ **Do** use flexible date matching from PDF_OPTIMIZATION.md

❌ **Don't** assume first table is correct (may be summary/index)  
✅ **Do** rely on intelligent table selection with scoring

❌ **Don't** use 0-indexed row numbers in config.json  
✅ **Do** use 1-indexed `tr_number` (matches table row display)

❌ **Don't** forget to update both config.json AND company_mapping  
✅ **Do** update all 3 locations when adding companies (config, mapping, supported list)
