# Financial Document Parser - API & UI

A comprehensive solution for extracting financial data from quarterly reports (PDF format) and converting them into structured JSON format with professional Excel/CSV export capabilities. This project includes a Flask REST API and a user-friendly Streamlit web interface.

## 🚀 Latest Updates

### v2.2 - AI-Powered Excel Generation 🤖 NEW!

- 🤖 **AI Extraction**: Use OpenAI GPT models to extract financial data from any PDF format (zero-config)
- 🎯 **Adaptive Parsing**: No need for company-specific configurations - works with any financial report
- 🔄 **Decoupled Workflow**: Parse once → Generate Excel multiple times with different methods
- 💡 **Smart Detection**: Automatically identifies all financial metrics and periods from tables
- 📊 **Dual Modes**: Choose between config-driven (fast, free) or AI-powered (adaptive, paid) extraction
- 💰 **Cost Efficient**: Uses GPT-4o-mini model (~$0.001-$0.003 per document)

See [AI_EXCEL_QUICKSTART.md](AI_EXCEL_QUICKSTART.md) for quick start guide.

### v2.1 - Excel/CSV Generation

- 📊 **Professional Excel Export**: Generate styled 47-row financial statements with borders, colors, and formatting
- 📄 **CSV Export**: Create matching CSV files for compatibility
- 🔢 **Indian Number Formatting**: Lakhs/crores style with comma separators and bracket negatives
- 💾 **File Management**: UUID-based storage with metadata tracking and download counts
- 🎨 **Professional Styling**: Bold headers, gray backgrounds, double underlines for totals
- 📁 **Dynamic Periods**: Auto-detects all available periods (not limited to 11 columns)

See [EXCEL_QUICKSTART.md](EXCEL_QUICKSTART.md) for quick start guide.

### v2.0 - Multi-Format PDF Support

- ✨ **Flexible Date Patterns**: Automatically detects various date formats and quarters
- 🎯 **Smart Page Detection**: Multi-priority page identification with fallback strategies
- 🔍 **Fuzzy Label Matching**: Robust extraction even when table structure varies
- 🏆 **Intelligent Table Selection**: Automatically selects the best table from multiple candidates
- 🛡️ **Enhanced Error Handling**: Retry logic and graceful degradation
- 📊 **Detailed Metadata**: Track extraction methods and processing details

See [PDF_OPTIMIZATION.md](PDF_OPTIMIZATION.md) for detailed documentation.

## Features

### PDF Parsing

- 🔍 **Automatic Page Detection**: Identifies standalone financial results pages with flexible patterns
- 📊 **Table Extraction**: Uses Docling to extract tables from PDFs with OCR support
- 🎯 **Smart Parsing**: Company-specific configurations with fuzzy matching fallback
- 🔄 **Multi-Format Support**: Handles various PDF layouts and date formats

### Excel/CSV Export

- 📊 **Professional Excel Files**: 47-row financial statement format with full styling
- 🤖 **AI-Powered Extraction**: Zero-config extraction using OpenAI GPT models
- 📄 **CSV Export**: Plain text format for easy data import
- 🔢 **Indian Formatting**: Comma separators (12,34,567) and bracket negatives (123)
- 🎯 **Dynamic Columns**: Auto-detects available periods (4-24 columns supported)
- 💾 **File Storage**: Save files with metadata for later download
- 📁 **File Management**: List, filter, download, and delete generated files

### User Interface

- ✏️ **Interactive Editing**: Review and edit extracted data in a tabular format
- 💾 **Version Control**: Save changes or create new edited versions
- 🌐 **REST API**: Flask-based API for programmatic access
- 💻 **Web UI**: Streamlit interface for easy document upload and visualization
- 📥 **Multiple Export Formats**: JSON, CSV, HTML, Markdown, and Excel

## Supported Companies

- Britannia
- Colgate
- Dabur
- HUL (Hindustan Unilever Limited)
- ITC
- Nestlé
- P&G (Procter & Gamble)

## Project Structure

```
docling_fin_parser/
├── app.py                  # Flask API server
├── streamlit_app.py        # Streamlit UI application
├── parser_core.py          # Core parsing functions
├── service.py              # Original CLI service
├── config.json             # Company-specific parsing configurations
├── requirements.txt        # Python dependencies
├── sample-data/            # Sample PDF files
├── output/                 # Generated output files
└── uploads/                # Temporary upload directory
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or navigate to the project directory**:

   ```bash
   cd d:\projects\docling_fin_parser
   ```

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:

   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Setup Environment Variables** (for AI features):

   Create a `.env` file in the project root:

   ```bash
   OPENAI_API_KEY=sk-your-api-key-here
   ```

   Get your API key from [platform.openai.com](https://platform.openai.com/api-keys)

   See [SETUP_ENV.md](SETUP_ENV.md) for detailed setup instructions.

## Usage

### Option 1: Using the Web UI (Streamlit)

This is the easiest way to use the service with a graphical interface.

1. **Start the Flask API** (in terminal 1):

   ```bash
   python app.py
   ```

   The API will start on `http://localhost:5000`

2. **Start the Streamlit UI** (in terminal 2):

   ```bash
   streamlit run streamlit_app.py
   ```

   The UI will open automatically in your browser at `http://localhost:8501`

3. **Use the interface**:
   - **Upload & Parse Tab**: Upload a PDF file, select the company name, and parse
   - **Review & Edit Tab**: View extracted data in an editable table, make corrections, and save changes
   - **View Results Tab**: See the final results and download in various formats

### Option 2: Using the REST API

For programmatic access or integration with other systems.

1. **Start the Flask API**:

   ```bash
   python app.py
   ```

2. **API Endpoints**:

   - **Health Check**:

     ```bash
     curl http://localhost:5000/health
     ```

   - **Get Supported Companies**:

     ```bash
     curl http://localhost:5000/api/companies
     ```

   - **Parse Document (Basic)**:

     ```bash
     curl -X POST http://localhost:5000/api/parse \
       -F "file=@sample-data/Britannia Unaudited Q2 June 2026.pdf" \
       -F "company_name=BRITANNIA"
     ```

   - **Parse Document (With Optimization Options)**:

     ```bash
     curl -X POST http://localhost:5000/api/parse \
       -F "file=@statement.pdf" \
       -F "company_name=HUL" \
       -F "prefer_standalone=true" \
       -F "use_fuzzy_matching=true"
     ```

   - **Download File**:
     ```bash
     curl http://localhost:5000/api/download/BRITANNIA_filename/filename.json -o output.json
     ```

## 🎯 Optimization Features

### Flexible Date Patterns

The parser now automatically detects various date formats:

- `30 June 2025`, `30.06.2025`, `30/06/2025`
- `June 30, 2025`, `Q2 2025`, `Q2 FY 2025`
- Works with any month, year, and quarter

No need to update code for different reporting periods!

### Smart Page Detection

Multi-priority page identification:

1. **Priority 1**: Explicit standalone statements (highest confidence)
2. **Priority 2**: Generic patterns without "consolidated" keyword
3. **Priority 3**: Generic patterns as fallback

### Fuzzy Label Matching

When exact row numbers don't match (PDF format changed):

- Automatically searches for labels in table text
- Uses fuzzy matching to handle OCR variations
- Tracks which method was used (see `extraction_method` in response)

### Intelligent Table Selection

When multiple tables are found:

- Scores tables based on content (financial keywords, row count, numeric data)
- Automatically selects the most likely financial statement
- Provides table selection details in response

### Test the Optimizations

```bash
# Test all sample PDFs with default optimization
python test_optimization.py

# Test different configurations on same PDF
python test_optimization.py --config-test
```

See [PDF_OPTIMIZATION.md](PDF_OPTIMIZATION.md) for complete documentation.

### Option 3: Using the Original CLI

For command-line usage without the API.

```bash
python service.py
```

Edit the `main()` function in `service.py` to change the input file and company name.

## Configuration

The `config.json` file contains company-specific parsing rules:

- **Column Layouts**: Define where data appears in tables
- **Financial Data Mappings**: Map table rows to financial metrics
- **Company-Specific Rules**: Each company has its own configuration

### Adding a New Company

1. Add a new column layout (if needed) in `column_layouts`
2. Create a new company configuration with:
   - `column_layout`: Reference to the layout
   - `financial_data`: List of metrics to extract with row numbers

Example:

```json
{
  "new_company": {
    "column_layout": "standard",
    "financial_data": [
      {
        "key": "revenue",
        "labels": ["Total Revenue"],
        "tr_number": 5
      }
    ]
  }
}
```

3. Update the company mapping in `parser_core.py`:

```python
company_mapping = {
    ...
    "NEWCOMPANY": "new_company"
}
```

## API Reference

### POST /api/parse

Parse a financial document with optimized multi-format support.

**Request (multipart/form-data)**:

- `file`: PDF file (required)
- `company_name`: Company name (required, e.g., "BRITANNIA")
- `prefer_standalone`: Prefer standalone over consolidated statements (optional, default: "true")
- `use_fuzzy_matching`: Enable fuzzy label matching fallback (optional, default: "true")

**Example using curl**:

```bash
curl -X POST http://localhost:5000/api/parse \
  -F "file=@statement.pdf" \
  -F "company_name=HUL" \
  -F "prefer_standalone=true" \
  -F "use_fuzzy_matching=true"
```

**Response**:

```json
{
  "success": true,
  "message": "Successfully processed document. Found 3 table(s), selected table 1.",
  "data": {
    "company_name": "BRITANNIA",
    "financial_data": [...],
    "metadata": {
      "source_file": "statement.pdf",
      "table_number": 1,
      "total_tables": 3,
      "extraction_method": "tr_number",
      "processing_time_seconds": 45.2
    }
  },
  "output_files": {
    "json": "path/to/file.json",
    "csv_1": "path/to/table-1.csv",
    "html_1": "path/to/table-1.html",
    "md_1": "path/to/table-1.md"
  },
  "processing_time": 45.2,
  "table_info": {
    "total_tables": 3,
    "selected_table": 1,
    "selection_method": "heuristic"
  }
}
```

### POST /api/generate-excel

Generate professionally formatted Excel file from JSON financial data.

**Request (application/json)**:

```json
{
  "company_name": "BRITANNIA",
  "financial_data": [...],
  "save": false  // Optional: save to storage (default: false)
}
```

**Example using curl**:

```bash
# Direct download
curl -X POST http://localhost:5000/api/generate-excel \
  -H "Content-Type: application/json" \
  -d @financial_data.json \
  --output statement.xlsx

# Save to storage
curl -X POST http://localhost:5000/api/generate-excel \
  -H "Content-Type: application/json" \
  -d '{"company_name": "BRITANNIA", "financial_data": [...], "save": true}'
```

**Response (save=false)**: Excel file download

**Response (save=true)**:

```json
{
  "success": true,
  "message": "Excel file generated and saved",
  "file_id": "abc123-def456-ghi789",
  "download_url": "/api/download-generated/abc123-def456-ghi789"
}
```

### POST /api/generate-csv

Generate CSV file from JSON financial data (same parameters as generate-excel).

### POST /api/generate-excel-ai 🤖 NEW!

Generate Excel file using AI extraction from previously parsed results.

**Request (application/json)**:

```json
{
  "company_name": "BRITANNIA",
  "document_name": "Britannia_Unaudited_Q2_June_2026",
  "preferred_format": "html", // Optional: "html" or "markdown" (default: "html")
  "save": false // Optional: save to storage (default: false)
}
```

**Example using curl**:

```bash
# Direct download
curl -X POST http://localhost:5000/api/generate-excel-ai \
  -H "Content-Type: application/json" \
  -d '{"company_name": "BRITANNIA", "document_name": "Britannia_Unaudited_Q2_June_2026"}' \
  --output statement.xlsx

# Save to storage
curl -X POST http://localhost:5000/api/generate-excel-ai \
  -H "Content-Type: application/json" \
  -d '{"company_name": "BRITANNIA", "document_name": "Britannia_Unaudited_Q2_June_2026", "save": true}'
```

**Response (save=false)**: Excel file download

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
    "tokens_used": 3500
  }
}
```

**Features**:

- ✅ No configuration needed - works with any financial report
- ✅ Automatically extracts all periods and metrics
- ✅ Uses previously saved HTML/Markdown from `/api/parse`
- ✅ Cost: ~$0.001-$0.003 per document

**Requirements**:

- Set `OPENAI_API_KEY` environment variable (see [SETUP_ENV.md](SETUP_ENV.md))
- Must run `/api/parse` first to save HTML/Markdown files

### GET /api/download-generated/<file_id>

Download previously generated Excel/CSV file.

**Query Parameters**:

- `preview`: Return metadata instead of file (optional, default: false)

**Response (preview=false)**: File download

**Response (preview=true)**:

```json
{
  "success": true,
  "file_info": {
    "file_id": "abc123-def456-ghi789",
    "company_name": "BRITANNIA",
    "file_type": "excel",
    "file_size": 25600,
    "download_count": 5
  }
}
```

### GET /api/list-generated-files

List all generated files with optional company filter.

**Query Parameters**:

- `company_name`: Filter by company (optional)

**Response**:

```json
{
  "success": true,
  "count": 3,
  "files": [
    {
      "file_id": "abc123...",
      "company_name": "BRITANNIA",
      "file_type": "excel",
      "file_size": 25600,
      "download_count": 5
    }
  ]
}
```

### DELETE /api/delete-generated/<file_id>

Delete generated Excel/CSV file from storage.

### GET /api/companies

Get list of supported companies.

**Response**:

```json
{
  "success": true,
  "companies": ["BRITANNIA", "COLGATE", "DABUR", "HUL", "ITC", "NESTLE", "P&G"]
}
```

### POST /api/update-financial-data

Update or edit financial data after parsing.

**Request Body** (JSON):

```json
{
  "company_name": "BRITANNIA",
  "document_name": "Britannia Unaudited Q2 June 2026",
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
  ],
  "create_new": false
}
```

**Response**:

```json
{
  "success": true,
  "message": "Financial data updated successfully",
  "file_path": "output/BRITANNIA_document/document-financial-data.json"
}
```

**Parameters**:

- `create_new`: Set to `true` to create a new edited version (saves as `*-financial-data-edited.json`), or `false` to overwrite the existing file

### GET /health

Check API health status.

**Response**:

```json
{
  "status": "healthy",
  "service": "Financial Document Parser API",
  "config_loaded": true
}
```

## Output Files

For each processed document, the following files are generated:

1. **JSON**: Structured financial data (`*-financial-data.json`)
2. **CSV**: Tabular data (`*-table-1.csv`)
3. **HTML**: Formatted table (`*-table-1.html`)
4. **Markdown**: Markdown table (`*-table-1.md`)
5. **Excel**: Professional 47-row financial statement (via API, optional)

## Excel/CSV Export

The Excel/CSV generation feature creates professionally formatted financial statements:

### Excel Format

- **Structure**: 47 rows × 12 columns (A-L)
- **Styling**: Bold headers, gray backgrounds, borders, double underlines
- **Formatting**: Indian number style with comma separators (12,34,567)
- **Negatives**: Bracket notation - `(123)` represents -123
- **Periods**: 11 columns from Jun 2025 to Dec 2022
- **Sections**: Revenue, Expenses, PBT, Tax, Net Profit, EBITDA, Growth

### Quick Start

```bash
# Install dependency
pip install openpyxl

# Generate Excel from JSON
curl -X POST http://localhost:5000/api/generate-excel \
  -H "Content-Type: application/json" \
  -d @financial_data.json \
  --output statement.xlsx
```

### Python Example

```python
import requests

# Generate Excel
with open('financial_data.json') as f:
    data = json.load(f)

response = requests.post(
    'http://localhost:5000/api/generate-excel',
    json=data
)

with open('statement.xlsx', 'wb') as f:
    f.write(response.content)
```

### Documentation

- **Quick Start**: [EXCEL_QUICKSTART.md](EXCEL_QUICKSTART.md)
- **Full API Docs**: [EXCEL_API_DOCUMENTATION.md](EXCEL_API_DOCUMENTATION.md)
- **Implementation**: [EXCEL_IMPLEMENTATION_SUMMARY.md](EXCEL_IMPLEMENTATION_SUMMARY.md)
- **Test Suite**: Run `python test_excel_api.py`
- **Examples**: Run `python example_excel_generation.py`

## Environment Variables

- `PORT`: API server port (default: 5000)
- `DEBUG`: Enable Flask debug mode (default: False)
- `OPENAI_API_KEY`: OpenAI API key for AI-powered extraction (required for AI features)
- `OPENAI_MODEL`: OpenAI model to use (optional, default: gpt-4o-mini)

**Setting up `.env` file**:

```bash
# Create .env file in project root
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4o-mini  # Optional
PORT=5000
DEBUG=False
```

See [SETUP_ENV.md](SETUP_ENV.md) for complete setup guide.

## Troubleshooting

### API Connection Error (Streamlit UI)

**Problem**: "Cannot connect to API server"

**Solution**:

1. Ensure the Flask API is running (`python app.py`)
2. Check that port 5000 is not blocked
3. Verify the API_URL in `streamlit_app.py` is correct

### OCR Issues

**Problem**: Poor table extraction or text recognition

**Solution**:

1. Ensure the PDF quality is good
2. Check that EasyOCR is properly installed
3. Try adjusting pipeline options in `parser_core.py`

### Memory Issues

**Problem**: Out of memory errors during processing

**Solution**:

1. Process one document at a time
2. Reduce the number of threads in `AcceleratorOptions`
3. Use CPU instead of GPU if GPU memory is limited

### Missing Dependencies

**Problem**: Import errors

**Solution**:

```bash
pip install -r requirements.txt --upgrade
```

## Development

### Running in Development Mode

```bash
# Flask API with auto-reload
DEBUG=true python app.py

# Streamlit with auto-reload (default behavior)
streamlit run streamlit_app.py
```

### Testing

```bash
# Test with sample data
python service.py

# Test API endpoint
curl -X POST http://localhost:5000/api/parse \
  -F "file=@sample-data/Britannia Unaudited Q2 June 2026.pdf" \
  -F "company_name=BRITANNIA"
```

## Performance

- Processing time: 30-60 seconds per document (CPU)
- Memory usage: ~2-4 GB during processing
- Supports PDFs up to 50MB

## Dependencies

Key dependencies:

- **docling**: PDF processing and table extraction
- **Flask**: REST API framework
- **Streamlit**: Web UI framework
- **pandas**: Data manipulation
- **BeautifulSoup4**: HTML parsing
- **EasyOCR**: Optical character recognition
- **pypdf**: PDF reading
- **openai**: OpenAI API client for AI-powered extraction
- **python-dotenv**: Environment variable management
- **openpyxl**: Excel file generation

See `requirements.txt` for complete list.

## License

This project is for internal use. Please ensure compliance with company policies and data handling guidelines.

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review the logs in the terminal
3. Contact the development team

## Future Enhancements

- [x] ~~Export to Excel format~~ ✅ Implemented (v2.1)
- [x] ~~AI-powered extraction~~ ✅ Implemented (v2.2)
- [ ] Support for consolidated financial statements
- [ ] Multi-year comparison views
- [ ] Batch processing of multiple documents
- [ ] Chart generation from financial data
- [ ] User authentication and session management
- [ ] Database storage for historical data
- [ ] Automated report generation
- [ ] Multi-language support for financial reports

---

**Note**: This tool is designed to extract data from standardized quarterly financial reports. Custom report formats may require configuration updates.
