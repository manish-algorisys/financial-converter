# AI Prompts for Financial Data Extraction

## Overview

This document contains reusable AI prompts for code generation, data extraction, and system improvements. Use these prompts with GitHub Copilot, ChatGPT, Claude, or other AI assistants.

---

## Table of Contents

1. [Financial Data Extraction Prompts](#financial-data-extraction-prompts)
2. [Code Generation Prompts](#code-generation-prompts)
3. [Testing & Debugging Prompts](#testing--debugging-prompts)
4. [System Enhancement Prompts](#system-enhancement-prompts)

---

## Financial Data Extraction Prompts

### Core System Prompt (Used in Production)

```
You are a financial data extraction specialist. Your task is to extract structured financial data from quarterly financial statements.

Extract the following financial metrics with their values for all available periods (quarters/years):
1. Revenue from operations (sale of goods, other operating revenues, total revenue)
2. Expenses (materials, inventories, employee benefits, finance costs, depreciation, other expenses)
3. Profit metrics (PBT, PAT, exceptional items)
4. Tax (current tax, deferred tax)
5. Other comprehensive income
6. EPS (basic and diluted)
7. Equity information

Return ONLY a valid JSON object with this exact structure:
{
  "company_name": "COMPANY_NAME",
  "financial_data": [
    {
      "particular": "Sale of goods",
      "key": "sale_of_goods",
      "values": {
        "30.06.2025": "1000.00",
        "31.03.2025": "950.00",
        "30.06.2024": "900.00",
        "31.03.2025_Y": "3800.00"
      }
    }
  ]
}

CRITICAL RULES:
- Use standard date formats: DD.MM.YYYY (e.g., "30.06.2025")
- For yearly/annual periods, append "_Y" suffix (e.g., "31.03.2025_Y")
- All values must be numeric strings (no currency symbols or commas in JSON)
- Negative values can be represented with minus sign or brackets: "(123)" = -123
- Use exact key names from the standard financial statement structure
- Include ALL periods found in the table
- If a value is not available, use empty string ""
- Do NOT include any explanatory text outside the JSON
```

**Usage Context:** This is embedded in [ai_extractor.py](ai_extractor.py#L27-L62) as `SYSTEM_PROMPT`.

---

## Code Generation Prompts

### Adding a New Company to Config

```
Add support for a new company called {COMPANY_NAME} to the financial parser system.

Requirements:
1. Update config.json with the company's financial data structure
2. Add company mapping in parser_core.py (line ~105)
3. Add to get_supported_companies() list (line ~487)
4. Use the "standard" column layout unless the PDF has a unique structure

Current config.json structure example:
{
  "company_name": {
    "column_layout": "standard",
    "financial_data": [
      {"key": "sale_of_goods", "labels": ["Sale of goods"], "tr_number": 5}
    ]
  }
}

Analyze the sample PDF at: sample-data/{COMPANY_NAME}_sample.pdf
Extract all 30+ financial line items with their exact labels and row numbers (1-indexed).
```

### Creating a New API Endpoint

```
Create a new Flask API endpoint for {FEATURE_DESCRIPTION}.

Follow the existing patterns in app.py:
1. Use @app.route decorator with appropriate HTTP method
2. Return consistent JSON structure: {"success": bool, "message": str, "data": {}}
3. Add comprehensive docstring describing parameters and returns
4. Include error handling with try/except and logging
5. Validate all required parameters at the start
6. Use _log.info() for operations and _log.error() for errors

Example response structure:
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {...},
  "metadata": {"processing_time": 1.23}
}

Reference existing endpoints: /api/parse, /api/generate-excel, /api/generate-excel-ai
```

### Enhancing the AI Extractor

```
Improve the AI financial data extractor to handle {SPECIFIC_CASE}.

Context:
- Current implementation: ai_extractor.py
- Uses OpenAI GPT-4o-mini for cost efficiency
- System prompt defines extraction rules
- Validates JSON structure with validate_financial_data()

Enhancement requirements:
1. Maintain backward compatibility with existing API
2. Add specific handling for {EDGE_CASE}
3. Update validation logic if needed
4. Add logging for new extraction method
5. Update metadata to track new approach

Test with: output/{COMPANY}_*/table-*.html files
```

---

## Testing & Debugging Prompts

### Debugging Fuzzy Matching Issues

```
Debug financial data extraction failures for {COMPANY_NAME}.

Investigation steps:
1. Check extraction_method in JSON response (tr_number vs fuzzy vs mixed)
2. Inspect HTML files in output/{COMPANY}_{DOC}/ directory
3. Review labels in config.json for the company
4. Enable debug logging: logging.basicConfig(level=logging.DEBUG)
5. Check table_info metadata for table selection details

Common issues:
- tr_number doesn't match PDF format → Use fuzzy matching
- Labels don't match HTML text → Update labels in config.json
- Wrong table selected → Adjust _select_best_table() scoring
- Date format mismatch → Check column_layout mapping

Provide analysis of: {ERROR_MESSAGE}
```

### Testing AI Extraction

```
Create comprehensive tests for AI-powered Excel generation.

Test cases:
1. Happy path: Standard quarterly report with all metrics
2. Edge case: Missing periods/values (should use "")
3. Edge case: Negative values in brackets "(123.45)"
4. Edge case: Very long table (>30000 chars, should truncate)
5. Error case: Invalid/corrupted HTML
6. Error case: No matching table files found
7. Validation: JSON structure matches schema
8. Validation: All required keys present
9. Performance: Token usage within expected range
10. Integration: Generated Excel renders correctly

Use pytest framework. Mock OpenAI API responses.
Files to test: ai_extractor.py, app.py (/api/generate-excel-ai)
```

---

## System Enhancement Prompts

### Optimizing OpenAI Token Usage

```
Optimize OpenAI API token usage in the financial extractor while maintaining accuracy.

Current usage: ~2000-5000 tokens per extraction

Optimization strategies:
1. Truncate HTML more intelligently (remove headers/footers)
2. Extract only <table> element instead of full HTML
3. Convert HTML to minimal Markdown before sending
4. Use function calling instead of JSON mode
5. Implement caching for similar documents
6. Batch multiple extractions in one request

Requirements:
- Maintain >95% extraction accuracy
- Reduce token usage by 30%+
- Add metrics tracking (tokens per extraction)
- Update metadata to include optimization method

Test with: 10 sample documents from output/ directory
```

### Adding New Output Formats

```
Add support for generating {NEW_FORMAT} files from financial data.

Follow the pattern in excel_generator.py:
1. Create new method: generate_{format}(json_data, output_path)
2. Use standard 47-row financial statement structure
3. Apply Indian number formatting (commas, bracket negatives)
4. Support all 11 period columns (30.06.2025 to 30.06.2023)
5. Add corresponding API endpoint in app.py
6. Update Streamlit UI with new generation option

Required features:
- Professional formatting/styling
- Support for metadata tracking via FileManager
- Direct download and save-to-storage modes
- Error handling and validation

Reference: generate_excel() and generate_csv() implementations
```

### Implementing Batch Processing

```
Add batch processing capability to parse multiple PDFs in one request.

Requirements:
1. New endpoint: POST /api/batch-parse
2. Accept array of files with company mappings
3. Process in parallel (max 3 concurrent)
4. Return aggregate results with individual status
5. Support partial success (some files succeed, others fail)
6. Track overall progress and timing

Input format:
{
  "files": [
    {"file": "britannia.pdf", "company_name": "BRITANNIA"},
    {"file": "colgate.pdf", "company_name": "COLGATE"}
  ],
  "options": {"prefer_standalone": true, "use_fuzzy_matching": true}
}

Response format:
{
  "success": true,
  "total": 2,
  "succeeded": 2,
  "failed": 0,
  "results": [
    {"file": "britannia.pdf", "success": true, "data": {...}},
    {"file": "colgate.pdf", "success": true, "data": {...}}
  ],
  "processing_time": 95.4
}

Consider: Rate limiting, memory management, timeout handling
```

---

## Prompt Engineering Best Practices

### For Financial Data Extraction

1. **Be Specific About Format:**

   - Specify exact JSON structure with examples
   - Define date format conventions (DD.MM.YYYY, \_Y suffix)
   - Clarify number representation (no commas in JSON values)

2. **Provide Context:**

   - Mention document type (quarterly financial statement)
   - Specify company name for context
   - Include all expected financial metrics

3. **Set Clear Boundaries:**

   - "Return ONLY JSON, no additional text"
   - Use response_format={"type": "json_object"} in API call
   - Validate with strict schema after extraction

4. **Handle Edge Cases:**
   - Missing values → use empty string ""
   - Negative values → accept both "-123" and "(123)"
   - Yearly periods → append "\_Y" suffix

### For Code Generation

1. **Reference Existing Patterns:**

   - Point to similar implementations in codebase
   - Specify file locations and line numbers
   - Request consistency with current architecture

2. **Define Success Criteria:**

   - Backward compatibility requirements
   - Performance benchmarks
   - Testing expectations

3. **Include Context Files:**
   - Attach relevant code snippets
   - Reference configuration files
   - Show expected input/output examples

---

## Example AI Conversations

### Example 1: Debugging Extraction Failure

**User:**

```
The AI extractor is failing for ITC Q2 2025 report. Error: "Invalid JSON response from OpenAI"
```

**AI Response Structure:**

```
Let me help debug this extraction failure:

1. First, check the raw HTML content:
   - Locate: output/ITC_ITC_Q2_2025/ITC_Q2_2025-table-1.html
   - Verify table structure is valid
   - Check for unusual characters or encoding issues

2. Review the truncation:
   - Current limit: 30000 chars
   - If HTML is large, important data might be truncated
   - Consider extracting <table> element only

3. Inspect OpenAI response:
   - Add logging before json.loads() in _extract_with_openai()
   - Check if response contains markdown code blocks
   - Verify _clean_json_response() is working

4. Test with simplified prompt:
   - Try with just first 5 metrics
   - Use gpt-4 instead of gpt-4o-mini for comparison
   - Lower temperature to 0.0

[Provides code fixes based on analysis]
```

### Example 2: Adding New Feature

**User:**

```
Add ability to compare financial data across multiple quarters in the Streamlit UI.
```

**AI Response Structure:**

```
I'll add a comparison feature with the following components:

1. New Streamlit Tab: "📈 Quarterly Comparison"
   - Select company and multiple documents
   - Choose metrics to compare (revenue, profit, etc.)
   - Display side-by-side table and charts

2. API Enhancement: GET /api/compare
   - Fetch multiple parsed results
   - Normalize periods for alignment
   - Calculate growth percentages

3. Visualization:
   - Line charts for trends
   - Bar charts for quarter comparison
   - Percentage change indicators

4. Implementation:
   [Provides complete code for all components]

5. Testing:
   [Provides test scenarios]
```

---

## Maintaining This Document

When adding new prompts:

1. **Categorize Appropriately:** Place in correct section
2. **Provide Context:** Link to relevant code files
3. **Include Examples:** Show expected input/output
4. **Test First:** Verify prompt works before documenting
5. **Update Regularly:** Review quarterly, remove outdated prompts

---

## Related Documentation

- [Copilot Instructions](.github/copilot-instructions.md) - Architecture and patterns
- [PDF Optimization](PDF_OPTIMIZATION.md) - Parsing strategies
- [Quick Reference](QUICK_REFERENCE.md) - Common commands
- [API Documentation](README.md) - Complete API reference

---

**Last Updated:** December 22, 2025  
**Maintainer:** Development Team
