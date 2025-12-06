# Financial Document Parser - API & UI

A comprehensive solution for extracting financial data from quarterly reports (PDF format) and converting them into structured JSON format. This project includes a Flask REST API and a user-friendly Streamlit web interface.

## Features

- 🔍 **Automatic Page Detection**: Identifies standalone financial results pages
- 📊 **Table Extraction**: Uses Docling to extract tables from PDFs with OCR support
- 🎯 **Smart Parsing**: Company-specific configurations for accurate data extraction
- ✏️ **Interactive Editing**: Review and edit extracted data in a tabular format
- 💾 **Version Control**: Save changes or create new edited versions
- 🌐 **REST API**: Flask-based API for programmatic access
- 💻 **Web UI**: Streamlit interface for easy document upload and visualization
- 📥 **Multiple Export Formats**: JSON, CSV, HTML, and Markdown

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

   - **Parse Document**:

     ```bash
     curl -X POST http://localhost:5000/api/parse \
       -F "file=@sample-data/Britannia Unaudited Q2 June 2026.pdf" \
       -F "company_name=BRITANNIA"
     ```

   - **Download File**:
     ```bash
     curl http://localhost:5000/api/download/BRITANNIA_filename/filename.json -o output.json
     ```

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

Parse a financial document.

**Request**:

- `file`: PDF file (multipart/form-data)
- `company_name`: Company name (string)

**Response**:

```json
{
  "success": true,
  "message": "Successfully processed document. Found 1 table(s).",
  "data": {
    "company_name": "BRITANNIA",
    "financial_data": [...]
  },
  "output_files": {
    "json": "path/to/file.json",
    "csv_1": "path/to/table.csv",
    "html_1": "path/to/table.html",
    "md_1": "path/to/table.md"
  },
  "processing_time": 45.2
}
```

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

## Environment Variables

- `PORT`: API server port (default: 5000)
- `DEBUG`: Enable Flask debug mode (default: False)

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

See `requirements.txt` for complete list.

## License

This project is for internal use. Please ensure compliance with company policies and data handling guidelines.

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review the logs in the terminal
3. Contact the development team

## Future Enhancements

- [ ] Support for consolidated financial statements
- [ ] Multi-year comparison views
- [ ] Batch processing of multiple documents
- [ ] Export to Excel format
- [ ] Chart generation from financial data
- [ ] User authentication and session management
- [ ] Database storage for historical data
- [ ] Automated report generation

---

**Note**: This tool is designed to extract data from standardized quarterly financial reports. Custom report formats may require configuration updates.
