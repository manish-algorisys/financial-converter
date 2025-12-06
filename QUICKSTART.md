# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Start the Services

#### Option A: Using the Launcher Script (Easiest)

**Windows:**

```bash
start.bat
```

**Linux/Mac:**

```bash
chmod +x start.sh
./start.sh
```

Then select option 3 to run both services.

#### Option B: Manual Start

**Terminal 1 - Flask API:**

```bash
python app.py
```

**Terminal 2 - Streamlit UI:**

```bash
streamlit run streamlit_app.py
```

### 3. Use the Application

1. Open your browser to `http://localhost:8501` (Streamlit will open automatically)
2. **Upload & Parse**: Upload a PDF file, select the company, and click "Parse Document"
3. **Review & Edit**: Switch to the "Review & Edit" tab to review and modify extracted data
4. **Save Changes**: Make edits and click "Save Changes" or "Save as New" to preserve edits
5. **Download**: Get the results in JSON, CSV, or Markdown formats

## 📋 Quick Examples

### Using the Web UI

**Tab 1: Upload & Parse**

1. Click "Browse files" and select a PDF
2. Choose company from dropdown (e.g., "BRITANNIA")
3. Click "🚀 Parse Document" button
4. View the extracted data preview

**Tab 2: Review & Edit** ⭐ NEW!

1. See all extracted data in an editable table
2. Click any cell to edit values
3. Add or remove rows as needed
4. Click "💾 Save Changes" to update the file
5. Or click "📄 Save as New" to create a separate edited version

**Tab 3: View Results**

1. See the final financial data
2. Download in JSON, CSV, or Markdown formats

### Using the API (cURL)

```bash
# Parse a document
curl -X POST http://localhost:5000/api/parse \
  -F "file=@sample-data/Britannia Unaudited Q2 June 2026.pdf" \
  -F "company_name=BRITANNIA"

# Get supported companies
curl http://localhost:5000/api/companies

# Check health
curl http://localhost:5000/health
```

### Using Python Requests

```python
import requests

# Parse document
with open('sample-data/Britannia Unaudited Q2 June 2026.pdf', 'rb') as f:
    files = {'file': f}
    data = {'company_name': 'BRITANNIA'}
    response = requests.post('http://localhost:5000/api/parse',
                           files=files, data=data)
    result = response.json()
    print(result)
```

## 🎯 Supported Companies

- BRITANNIA
- COLGATE
- DABUR
- HUL
- ITC
- NESTLE
- P&G

## 📁 Where Are My Files?

All output files are saved in the `output/` directory:

```
output/
├── BRITANNIA_DocumentName/
│   ├── DocumentName-financial-data.json
│   ├── DocumentName-table-1.csv
│   ├── DocumentName-table-1.html
│   └── DocumentName-table-1.md
```

## ⚡ Tips

- **Processing Time**: Typically 30-60 seconds per document
- **File Size**: PDFs up to 50MB are supported
- **Quality**: Better PDF quality = better extraction results
- **Parallel Processing**: Process one document at a time for best results

## 🔧 Troubleshooting

### "API is not running"

- Make sure Flask API is started first: `python app.py`
- Check if port 5000 is available

### "Module not found"

- Activate virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
- Reinstall: `pip install -r requirements.txt`

### Slow Processing

- Normal for first run (model loading)
- Subsequent runs are faster
- Use CPU mode if GPU causes issues

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check `config.json` to add new companies
- Explore the API endpoints for integration

## 💡 Need Help?

1. Check the logs in the terminal
2. Review the [README.md](README.md) troubleshooting section
3. Ensure all dependencies are installed correctly

---

**Happy Parsing! 📊**
