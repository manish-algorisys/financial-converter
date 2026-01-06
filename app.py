"""
Flask API for Financial Document Parser Service
"""
import os
import json
import logging
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import shutil
from dotenv import load_dotenv
from pypdf import PdfReader
import re
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

from parser_core import (
    process_pdf_document,
    load_config,
    get_supported_companies
)
from excel_generator import FinancialExcelGenerator, FileManager
from ai_extractor import AIFinancialExtractor, validate_financial_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
_log = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = Path('uploads')
OUTPUT_FOLDER = Path('output')
EXCEL_STORAGE_FOLDER = Path('excel_storage')
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
EXCEL_STORAGE_FOLDER.mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['EXCEL_STORAGE_FOLDER'] = EXCEL_STORAGE_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize file manager
file_manager = FileManager(EXCEL_STORAGE_FOLDER)

# Initialize AI extractor (optional - requires OPENAI_API_KEY)
try:
    ai_extractor = AIFinancialExtractor()
    _log.info("AI extractor initialized successfully")
except Exception as e:
    _log.warning(f"AI extractor not available: {str(e)}")
    ai_extractor = None

# Load configuration
try:
    config = load_config()
    _log.info("Configuration loaded successfully")
except Exception as e:
    _log.error(f"Failed to load configuration: {str(e)}")
    config = None


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def detect_company_name_from_pdf(pdf_path):
    """
    Detect company name from PDF file content.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Detected company name or None if not found
    """
    try:
        # Company name patterns for matching
        company_patterns = {
            'BRITANNIA': [r'britannia', r'britannia\s+industries'],
            'COLGATE': [r'colgate', r'colgate-palmolive', r'colgate\s+palmolive'],
            'DABUR': [r'dabur', r'dabur\s+india'],
            'HUL': [r'hindustan\s+unilever', r'hul', r'unilever'],
            'ITC': [r'\bitc\b', r'itc\s+limited', r'i\.t\.c'],
            'NESTLE': [r'nestle', r'nestlé', r'nestle\s+india'],
            'P&G': [r'procter\s+&\s+gamble', r'procter\s+and\s+gamble', r'p&g', r'p\s+&\s+g'],
        }
        
        supported_companies = get_supported_companies()
        
        # Read PDF content
        try:
            reader = PdfReader(str(pdf_path))
        except Exception as pdf_error:
            _log.error(f"Cannot read PDF file (corrupted or invalid): {str(pdf_error)}")
            return None
        
        # Extract text from first few pages
        text = ""
        for page_num in range(min(3, len(reader.pages))):
            try:
                text += reader.pages[page_num].extract_text() or ""
            except Exception as page_error:
                _log.warning(f"Error reading page {page_num + 1}: {str(page_error)}")
                continue
        
        text_lower = text.lower()
        
        # Try to match company patterns
        for company, patterns in company_patterns.items():
            if company in supported_companies:
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        _log.info(f"Auto-detected company: {company}")
                        return company
        
        _log.warning("Could not auto-detect company name from PDF")
        return None
    except Exception as e:
        _log.error(f"Error detecting company name: {str(e)}")
        return None


def scan_folder_for_pdfs(folder_path):
    """
    Scan folder for PDF files.
    
    Args:
        folder_path: Path to folder
    
    Returns:
        Dictionary with success status and list of PDF files
    """
    try:
        folder = Path(folder_path)
        if not folder.exists():
            return {'success': False, 'error': f'Folder does not exist: {folder_path}'}
        if not folder.is_dir():
            return {'success': False, 'error': f'Path is not a directory: {folder_path}'}
        
        pdf_files = list(folder.glob('*.pdf'))
        if not pdf_files:
            return {'success': False, 'error': f'No PDF files found in: {folder_path}'}
        
        return {'success': True, 'files': pdf_files, 'count': len(pdf_files)}
    except Exception as e:
        return {'success': False, 'error': f'Error scanning folder: {str(e)}'}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Financial Document Parser API',
        'config_loaded': config is not None
    }), 200


@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Get list of supported companies."""
    try:
        companies = get_supported_companies()
        return jsonify({
            'success': True,
            'companies': companies
        }), 200
    except Exception as e:
        _log.error(f"Error getting companies: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/parse', methods=['POST'])
def parse_document():
    """
    Parse financial document with optimized multi-format support and auto-detection.
    
    Expected form data:
    - file: PDF file (required)
    - company_name: Company name (optional - will auto-detect if not provided)
    - prefer_standalone: Prefer standalone over consolidated statements (optional, default: true)
    - use_fuzzy_matching: Enable fuzzy label matching fallback (optional, default: true)
    
    Returns:
    - success: bool
    - message: str
    - data: Parsed financial data
    - output_files: Generated file paths
    - processing_time: Processing duration
    - table_info: Table selection metadata (total_tables, selected_table, selection_method)
    - detected_company: Auto-detected company name (if auto-detection was used)
    """
    try:
        # Check if config is loaded
        if config is None:
            return jsonify({
                'success': False,
                'error': 'Configuration not loaded'
            }), 500
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only PDF files are allowed.'
            }), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_dir = Path(tempfile.mkdtemp())
        file_path = temp_dir / filename
        file.save(str(file_path))
        
        # Get or detect company name
        company_name = request.form.get('company_name', '').upper()
        detected_company = None
        
        if not company_name:
            # Auto-detect company name
            _log.info(f"No company name provided, attempting auto-detection for: {filename}")
            detected_company = detect_company_name_from_pdf(file_path)
            
            if not detected_company:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return jsonify({
                    'success': False,
                    'error': 'Could not auto-detect company name. Please provide company_name parameter.'
                }), 400
            
            company_name = detected_company
            _log.info(f"Auto-detected company: {company_name}")
        
        # Validate company name
        if company_name not in get_supported_companies():
            shutil.rmtree(temp_dir, ignore_errors=True)
            return jsonify({
                'success': False,
                'error': f'Unsupported company: {company_name}. Supported: {get_supported_companies()}'
            }), 400
        
        # Get optional optimization parameters
        prefer_standalone = request.form.get('prefer_standalone', 'true').lower() == 'true'
        use_fuzzy_matching = request.form.get('use_fuzzy_matching', 'true').lower() == 'true'
        
        _log.info(f"Processing file: {filename} for company: {company_name}")
        if detected_company:
            _log.info(f"Company auto-detected: {detected_company}")
        _log.info(f"Options: prefer_standalone={prefer_standalone}, use_fuzzy_matching={use_fuzzy_matching}")
        
        # Create output directory for this request
        output_dir = OUTPUT_FOLDER / f"{company_name}_{file_path.stem}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process document with optimization parameters
        result = process_pdf_document(
            pdf_path=file_path,
            company_name=company_name,
            output_dir=output_dir,
            config=config,
            prefer_standalone=prefer_standalone,
            use_fuzzy_matching=use_fuzzy_matching
        )
        
        # Clean up temporary file
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        if result['success']:
            response_data = {
                'success': True,
                'message': result['message'],
                'data': result['json_result'],
                'output_files': result['output_files'],
                'processing_time': result.get('processing_time'),
                'table_info': result.get('table_info', {})
            }
            
            # Include detected company if auto-detection was used
            if detected_company:
                response_data['detected_company'] = detected_company
            
            return jsonify(response_data), 200
        else:
            return jsonify({
                'success': False,
                'error': result['message']
            }), 500
            
    except Exception as e:
        _log.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/parse-batch', methods=['POST'])
def parse_batch_documents():
    """
    Parse multiple PDF documents in batch with auto-detection.
    
    Expected form data:
    - files[]: Multiple PDF files (required)
    - prefer_standalone: Prefer standalone over consolidated statements (optional, default: true)
    - use_fuzzy_matching: Enable fuzzy label matching fallback (optional, default: true)
    
    Returns:
    - success: bool
    - message: str
    - results: Array of processing results for each file
    - summary: Statistics (total, successful, failed)
    """
    try:
        if config is None:
            return jsonify({
                'success': False,
                'error': 'Configuration not loaded'
            }), 500
        
        # Get all uploaded files
        files = request.files.getlist('files[]')
        
        if not files or len(files) == 0:
            return jsonify({
                'success': False,
                'error': 'No files provided'
            }), 400
        
        # Get optional parameters
        prefer_standalone = request.form.get('prefer_standalone', 'true').lower() == 'true'
        use_fuzzy_matching = request.form.get('use_fuzzy_matching', 'true').lower() == 'true'
        
        _log.info(f"Batch processing {len(files)} files")
        
        results = []
        successful = 0
        failed = 0
        
        for file in files:
            if file.filename == '':
                results.append({
                    'filename': 'unknown',
                    'success': False,
                    'error': 'Empty filename'
                })
                failed += 1
                continue
            
            if not allowed_file(file.filename):
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': 'Invalid file type'
                })
                failed += 1
                continue
            
            try:
                # Save file temporarily
                filename = secure_filename(file.filename)
                temp_dir = Path(tempfile.mkdtemp())
                file_path = temp_dir / filename
                file.save(str(file_path))
                
                # Auto-detect company name
                detected_company = detect_company_name_from_pdf(file_path)
                
                if not detected_company:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    results.append({
                        'filename': filename,
                        'success': False,
                        'error': 'Could not auto-detect company name'
                    })
                    failed += 1
                    continue
                
                # Create output directory
                output_dir = OUTPUT_FOLDER / f"{detected_company}_{file_path.stem}"
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Process document
                result = process_pdf_document(
                    pdf_path=file_path,
                    company_name=detected_company,
                    output_dir=output_dir,
                    config=config,
                    prefer_standalone=prefer_standalone,
                    use_fuzzy_matching=use_fuzzy_matching
                )
                
                # Clean up
                shutil.rmtree(temp_dir, ignore_errors=True)
                
                if result['success']:
                    results.append({
                        'filename': filename,
                        'success': True,
                        'detected_company': detected_company,
                        'message': result['message'],
                        'data': result['json_result'],
                        'output_files': result['output_files'],
                        'processing_time': result.get('processing_time'),
                        'table_info': result.get('table_info', {})
                    })
                    successful += 1
                else:
                    results.append({
                        'filename': filename,
                        'success': False,
                        'detected_company': detected_company,
                        'error': result['message']
                    })
                    failed += 1
                    
            except Exception as e:
                _log.error(f"Error processing {file.filename}: {str(e)}")
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': str(e)
                })
                failed += 1
        
        return jsonify({
            'success': True,
            'message': f'Batch processing completed',
            'results': results,
            'summary': {
                'total': len(files),
                'successful': successful,
                'failed': failed
            }
        }), 200
        
    except Exception as e:
        _log.error(f"Error in batch processing: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Batch processing error: {str(e)}'
        }), 500


@app.route('/api/parse-folder', methods=['POST'])
def parse_folder_documents():
    """
    Parse all PDF documents in a folder with auto-detection.
    
    Expected JSON body:
    {
        "folder_path": "/path/to/pdfs",
        "prefer_standalone": true,
        "use_fuzzy_matching": true
    }
    
    Returns:
    - success: bool
    - message: str
    - results: Array of processing results for each file
    - summary: Statistics (total, successful, failed)
    """
    try:
        if config is None:
            return jsonify({
                'success': False,
                'error': 'Configuration not loaded'
            }), 500
        
        data = request.get_json()
        
        if not data or 'folder_path' not in data:
            return jsonify({
                'success': False,
                'error': 'folder_path not provided'
            }), 400
        
        folder_path = data.get('folder_path')
        prefer_standalone = data.get('prefer_standalone', True)
        use_fuzzy_matching = data.get('use_fuzzy_matching', True)
        
        # Scan folder for PDFs
        scan_result = scan_folder_for_pdfs(folder_path)
        
        if not scan_result['success']:
            return jsonify({
                'success': False,
                'error': scan_result['error']
            }), 400
        
        pdf_files = scan_result['files']
        _log.info(f"Found {len(pdf_files)} PDF files in folder: {folder_path}")
        
        results = []
        successful = 0
        failed = 0
        
        for pdf_path in pdf_files:
            try:
                # Auto-detect company name
                detected_company = detect_company_name_from_pdf(pdf_path)
                
                if not detected_company:
                    results.append({
                        'filename': pdf_path.name,
                        'success': False,
                        'error': 'Could not auto-detect company name'
                    })
                    failed += 1
                    continue
                
                # Create output directory
                output_dir = OUTPUT_FOLDER / f"{detected_company}_{pdf_path.stem}"
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Process document
                result = process_pdf_document(
                    pdf_path=pdf_path,
                    company_name=detected_company,
                    output_dir=output_dir,
                    config=config,
                    prefer_standalone=prefer_standalone,
                    use_fuzzy_matching=use_fuzzy_matching
                )
                
                if result['success']:
                    results.append({
                        'filename': pdf_path.name,
                        'success': True,
                        'detected_company': detected_company,
                        'message': result['message'],
                        'data': result['json_result'],
                        'output_files': result['output_files'],
                        'processing_time': result.get('processing_time'),
                        'table_info': result.get('table_info', {})
                    })
                    successful += 1
                else:
                    results.append({
                        'filename': pdf_path.name,
                        'success': False,
                        'detected_company': detected_company,
                        'error': result['message']
                    })
                    failed += 1
                    
            except Exception as e:
                _log.error(f"Error processing {pdf_path.name}: {str(e)}")
                results.append({
                    'filename': pdf_path.name,
                    'success': False,
                    'error': str(e)
                })
                failed += 1
        
        return jsonify({
            'success': True,
            'message': f'Folder processing completed',
            'results': results,
            'summary': {
                'total': len(pdf_files),
                'successful': successful,
                'failed': failed
            }
        }), 200
        
    except Exception as e:
        _log.error(f"Error in folder processing: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Folder processing error: {str(e)}'
        }), 500


@app.route('/api/download/<path:filename>', methods=['GET'])
def download_file(filename):
    """Download generated file."""
    try:
        file_path = OUTPUT_FOLDER / filename
        
        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_path.name
        )
    except Exception as e:
        _log.error(f"Error downloading file: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/results/<company_name>/<document_name>', methods=['GET'])
def get_results(company_name, document_name):
    """Get parsing results for a specific document."""
    try:
        output_dir = OUTPUT_FOLDER / f"{company_name}_{document_name}"
        json_file = output_dir / f"{document_name}-financial-data.json"
        
        if not json_file.exists():
            return jsonify({
                'success': False,
                'error': 'Results not found'
            }), 404
        
        import json
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        _log.error(f"Error getting results: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/update-financial-data', methods=['POST'])
def update_financial_data():
    """
    Update financial data JSON file after editing.
    
    Expected JSON body:
    {
        "company_name": "BRITANNIA",
        "document_name": "Britannia Unaudited Q2 June 2026",
        "financial_data": [...],  # Updated financial data array
        "create_new": false  # Optional: if true, creates a new edited version
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        company_name = data.get('company_name', '').upper()
        document_name = data.get('document_name', '')
        financial_data = data.get('financial_data', [])
        create_new = data.get('create_new', False)
        
        if not company_name or not document_name:
            return jsonify({
                'success': False,
                'error': 'Company name and document name are required'
            }), 400
        
        if not financial_data:
            return jsonify({
                'success': False,
                'error': 'Financial data is required'
            }), 400
        
        # Validate company name
        if company_name not in get_supported_companies():
            return jsonify({
                'success': False,
                'error': f'Unsupported company: {company_name}'
            }), 400
        
        # Prepare updated data
        updated_data = {
            "company_name": company_name,
            "financial_data": financial_data
        }
        
        # Determine output path
        output_dir = OUTPUT_FOLDER / f"{company_name}_{document_name}"
        
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        
        if create_new:
            # Create a new edited version
            json_file = output_dir / f"{document_name}-financial-data-edited.json"
        else:
            # Overwrite existing file
            json_file = output_dir / f"{document_name}-financial-data.json"
        
        # Save updated JSON
        import json
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        _log.info(f"Updated financial data saved to {json_file}")
        
        return jsonify({
            'success': True,
            'message': 'Financial data updated successfully',
            'file_path': str(json_file)
        }), 200
        
    except Exception as e:
        _log.error(f"Error updating financial data: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/generate-excel', methods=['POST'])
def generate_excel():
    """
    Generate Excel file from JSON financial data.
    
    Expected JSON body:
    {
        "financial_data": [...],  # Financial data array
        "company_name": "BRITANNIA",  # Optional, defaults from data
        "save": true  # Optional: save to storage (default: false)
    }
    
    Returns:
    - Excel file download OR
    - File ID if save=true
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate input
        if 'financial_data' not in data or not data['financial_data']:
            # Check if full JSON format with company_name and financial_data
            if 'company_name' not in data:
                return jsonify({
                    'success': False,
                    'error': 'financial_data array is required'
                }), 400
        
        # Prepare JSON data
        json_data = {
            'company_name': data.get('company_name', 'Financial Statement'),
            'financial_data': data.get('financial_data', [])
        }
        
        # Generate Excel
        generator = FinancialExcelGenerator()
        temp_dir = Path(tempfile.mkdtemp())
        company_name_safe = json_data['company_name'].replace(' ', '_')
        excel_file = temp_dir / f"{company_name_safe}_financial_statement.xlsx"
        
        success = generator.generate_excel(json_data, excel_file)
        
        if not success:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return jsonify({
                'success': False,
                'error': 'Failed to generate Excel file'
            }), 500
        
        # Check if we should save to storage
        save_to_storage = data.get('save', False)
        
        if save_to_storage:
            # Save to storage and return file ID
            file_id = file_manager.save_file(excel_file, json_data['company_name'], 'excel')
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return jsonify({
                'success': True,
                'message': 'Excel file generated and saved',
                'file_id': file_id,
                'download_url': f'/api/download-generated/{file_id}'
            }), 200
        else:
            # Return file directly
            try:
                return send_file(
                    excel_file,
                    as_attachment=True,
                    download_name=excel_file.name,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            finally:
                # Clean up temp file after sending
                import atexit
                atexit.register(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
        
    except Exception as e:
        _log.error(f"Error generating Excel: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/generate-csv', methods=['POST'])
def generate_csv():
    """
    Generate CSV file from JSON financial data.
    
    Expected JSON body:
    {
        "financial_data": [...],  # Financial data array
        "company_name": "BRITANNIA",  # Optional, defaults from data
        "save": true  # Optional: save to storage (default: false)
    }
    
    Returns:
    - CSV file download OR
    - File ID if save=true
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate input
        if 'financial_data' not in data or not data['financial_data']:
            if 'company_name' not in data:
                return jsonify({
                    'success': False,
                    'error': 'financial_data array is required'
                }), 400
        
        # Prepare JSON data
        json_data = {
            'company_name': data.get('company_name', 'Financial Statement'),
            'financial_data': data.get('financial_data', [])
        }
        
        # Generate CSV
        generator = FinancialExcelGenerator()
        temp_dir = Path(tempfile.mkdtemp())
        company_name_safe = json_data['company_name'].replace(' ', '_')
        csv_file = temp_dir / f"{company_name_safe}_financial_statement.csv"
        
        success = generator.generate_csv(json_data, csv_file)
        
        if not success:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return jsonify({
                'success': False,
                'error': 'Failed to generate CSV file'
            }), 500
        
        # Check if we should save to storage
        save_to_storage = data.get('save', False)
        
        if save_to_storage:
            # Save to storage and return file ID
            file_id = file_manager.save_file(csv_file, json_data['company_name'], 'csv')
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return jsonify({
                'success': True,
                'message': 'CSV file generated and saved',
                'file_id': file_id,
                'download_url': f'/api/download-generated/{file_id}'
            }), 200
        else:
            # Return file directly
            try:
                return send_file(
                    csv_file,
                    as_attachment=True,
                    download_name=csv_file.name,
                    mimetype='text/csv'
                )
            finally:
                # Clean up temp file after sending
                import atexit
                atexit.register(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
        
    except Exception as e:
        _log.error(f"Error generating CSV: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/generate-excel-ai', methods=['POST'])
def generate_excel_ai():
    """
    Generate Excel file using AI extraction from previously parsed results.
    
    Expected request:
    - JSON body OR multipart/form-data
    - JSON fields:
        {
            "company_name": "BRITANNIA",
            "document_name": "Britannia_Unaudited_Q2_June_2026",  // Output directory name
            "preferred_format": "html",  // Optional: "html" or "markdown" (default: "html")
            "save": false  // Optional: save to storage (default: false)
        }
    - Optional multipart field:
        "template_excel": Excel template file with placeholders ({{key[period]}} format)
    
    Returns:
    - Excel file download OR
    - File ID if save=true
    """
    template_temp_path = None
    
    try:
        # Check if AI extractor is available
        if ai_extractor is None:
            return jsonify({
                'success': False,
                'error': 'AI extraction not available. Please set OPENAI_API_KEY environment variable.'
            }), 503
        
        # Handle multipart (with template) or JSON request
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Extract data from form fields
            company_name = request.form.get('company_name', '').upper()
            document_name = request.form.get('document_name', '')
            preferred_format = request.form.get('preferred_format', 'html').lower()
            save_to_storage = request.form.get('save', 'false').lower() == 'true'
            
            data = {
                'company_name': company_name,
                'document_name': document_name,
                'preferred_format': preferred_format,
                'save': save_to_storage
            }
            
            # Check for template Excel file
            if 'template_excel' in request.files:
                template_file = request.files['template_excel']
                if template_file.filename:
                    # Save template to temporary location
                    temp_dir = Path(tempfile.mkdtemp())
                    template_temp_path = temp_dir / secure_filename(template_file.filename)
                    template_file.save(template_temp_path)
                    _log.info(f"Template Excel uploaded: {template_file.filename}")
        else:
            # Standard JSON request
            data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        company_name = data.get('company_name', '').upper()
        document_name = data.get('document_name', '')
        preferred_format = data.get('preferred_format', 'html').lower()
        
        if not company_name or not document_name:
            return jsonify({
                'success': False,
                'error': 'company_name and document_name are required'
            }), 400
        
        # Validate company name
        if company_name not in get_supported_companies():
            return jsonify({
                'success': False,
                'error': f'Unsupported company: {company_name}'
            }), 400
        
        # Locate output directory
        output_dir = OUTPUT_FOLDER / f"{company_name}_{document_name}"
        
        if not output_dir.exists():
            return jsonify({
                'success': False,
                'error': f'No parsed results found for {company_name}/{document_name}'
            }), 404
        
        _log.info(f"Extracting financial data using AI for {company_name}/{document_name}")
        
        # Extract data using AI
        try:
            extracted_data = ai_extractor.extract_from_output_dir(
                output_dir, 
                company_name,
                preferred_format=preferred_format
            )
            
            # Validate extracted data
            validate_financial_data(extracted_data)
            
        except FileNotFoundError as e:
            return jsonify({
                'success': False,
                'error': f'No suitable table files found: {str(e)}'
            }), 404
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': f'Invalid data extracted: {str(e)}'
            }), 500
        
        # Generate Excel from AI-extracted data
        generator = FinancialExcelGenerator()
        temp_dir = Path(tempfile.mkdtemp())
        company_name_safe = company_name.replace(' ', '_')
        excel_file = temp_dir / f"{company_name_safe}_AI_financial_statement.xlsx"
        
        # Use template if provided, otherwise use fixed format
        if template_temp_path:
            _log.info(f"Using Excel template for Excel generation: {template_temp_path.name}")
            success = generator.generate_excel(extracted_data, excel_file, template_excel_path=template_temp_path)
            template_used = True
        else:
            success = generator.generate_excel(extracted_data, excel_file)
            template_used = False
        
        if not success:
            # Clean up temp files
            shutil.rmtree(temp_dir, ignore_errors=True)
            if template_temp_path and template_temp_path.parent.exists():
                shutil.rmtree(template_temp_path.parent, ignore_errors=True)
            return jsonify({
                'success': False,
                'error': 'Failed to generate Excel file from AI-extracted data'
            }), 500
        
        # Check if we should save to storage
        save_to_storage = data.get('save', False)
        
        if save_to_storage:
            # Save to storage and return file ID
            file_id = file_manager.save_file(excel_file, company_name, 'excel')
            shutil.rmtree(temp_dir, ignore_errors=True)
            # Clean up template temp file
            if template_temp_path and template_temp_path.parent.exists():
                shutil.rmtree(template_temp_path.parent, ignore_errors=True)
            
            return jsonify({
                'success': True,
                'message': 'Excel file generated using AI and saved',
                'file_id': file_id,
                'download_url': f'/api/download-generated/{file_id}',
                'metadata': extracted_data.get('metadata', {}),
                'used_template': template_used
            }), 200
        else:
            # Return file directly
            try:
                return send_file(
                    excel_file,
                    as_attachment=True,
                    download_name=excel_file.name,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            finally:
                # Clean up temp files after sending
                import atexit
                def cleanup():
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    if template_temp_path and template_temp_path.parent.exists():
                        shutil.rmtree(template_temp_path.parent, ignore_errors=True)
                atexit.register(cleanup)
        
    except Exception as e:
        # Clean up on error
        if template_temp_path and template_temp_path.parent.exists():
            shutil.rmtree(template_temp_path.parent, ignore_errors=True)
        _log.error(f"Error generating AI Excel: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/generate-excel-ai-consolidated', methods=['POST'])
def generate_excel_ai_consolidated():
    """
    Generate consolidated Excel from multiple parsed documents using AI extraction.
    
    Expected Form Data:
    - documents: JSON string array of [{company, document}, ...]
    - preferred_format: 'html' or 'markdown' (default: 'html')
    - save: 'true' to save to storage, 'false' to return file directly (default: 'false')
    - template_excel: Optional Excel template file
    
    Returns:
    - Excel file or file_id based on save parameter
    """
    try:
        data = request.form
        
        # Parse documents array
        try:
            documents = json.loads(data.get('documents', '[]'))
        except:
            return jsonify({
                'success': False,
                'error': 'Invalid documents parameter - must be JSON array'
            }), 400
        
        if not documents or not isinstance(documents, list):
            return jsonify({
                'success': False,
                'error': 'No documents provided or invalid format'
            }), 400
        
        preferred_format = data.get('preferred_format', 'html').lower()
        if preferred_format not in ['html', 'markdown']:
            return jsonify({
                'success': False,
                'error': 'Invalid format - must be html or markdown'
            }), 400
        
        # Handle optional template
        template_temp_path = None
        if 'template_excel' in request.files:
            template_file = request.files['template_excel']
            if template_file and template_file.filename:
                # Save template to temp location
                import tempfile
                temp_template_dir = Path(tempfile.mkdtemp())
                template_temp_path = temp_template_dir / secure_filename(template_file.filename)
                template_file.save(str(template_temp_path))
        
        # Extract data from all documents
        companies_data = []
        total_tokens = 0
        
        for doc_info in documents:
            company_name = doc_info.get('company', '').upper()
            document_name = doc_info.get('document', '')
            
            if not company_name or not document_name:
                continue
            
            # Find the output directory for this document
            output_dir = OUTPUT_FOLDER / f"{company_name}_{document_name}"
            
            if not output_dir.exists():
                _log.warning(f"Output directory not found: {output_dir}")
                continue
            
            # Extract data using AI
            extractor = AIFinancialExtractor()
            source_format = 'html' if preferred_format == 'html' else 'markdown'
            
            try:
                # Pass template to extractor for guided extraction
                extracted_data = extractor.extract_from_output_dir(
                    output_dir, 
                    company_name, 
                    source_format,
                    template_excel_path=template_temp_path  # NEW: Template-guided extraction
                )
                
                if extracted_data and isinstance(extracted_data, dict):
                    _log.info(f"Extracted data for {company_name}/{document_name}")
                    # Add company metadata
                    extracted_data['company_name'] = company_name
                    extracted_data['document_name'] = document_name
                    companies_data.append(extracted_data)
                    
                    # Track tokens
                    metadata = extracted_data.get('metadata', {})
                    total_tokens += metadata.get('tokens_used', 0)
                else:
                    _log.warning(f"No data extracted for {company_name}/{document_name}")
            except Exception as extract_error:
                _log.error(f"Error extracting data for {company_name}/{document_name}: {extract_error}")
                continue
        
        _log.info(f"Total companies with extracted data: {len(companies_data)}")
        if not companies_data:
            # Clean up template if exists
            if template_temp_path and template_temp_path.parent.exists():
                shutil.rmtree(template_temp_path.parent, ignore_errors=True)
            _log.error("No valid data extracted from any document")
            return jsonify({
                'success': False,
                'error': 'No valid data extracted from any document. Please ensure documents have been parsed and AI extraction is working.'
            }), 400
        
        # Generate consolidated Excel
        temp_dir = Path(tempfile.mkdtemp())
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_file = temp_dir / f"Consolidated_{timestamp}.xlsx"
        
        generator = FinancialExcelGenerator()
        template_used = False
        
        if template_temp_path and template_temp_path.exists():
            # Use template
            success = generator.generate_excel_consolidated(
                companies_data, excel_file, template_temp_path
            )
            template_used = True
        else:
            # Use default format
            success = generator.generate_excel_consolidated(
                companies_data, excel_file
            )
        
        if not success:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
            if template_temp_path and template_temp_path.parent.exists():
                shutil.rmtree(template_temp_path.parent, ignore_errors=True)
            return jsonify({
                'success': False,
                'error': 'Failed to generate consolidated Excel file'
            }), 500
        
        # Check if we should save to storage
        save_to_storage = data.get('save', 'false').lower() == 'true'
        
        if save_to_storage:
            # Save to storage
            file_id = file_manager.save_file(excel_file, 'CONSOLIDATED', 'excel')
            shutil.rmtree(temp_dir, ignore_errors=True)
            if template_temp_path and template_temp_path.parent.exists():
                shutil.rmtree(template_temp_path.parent, ignore_errors=True)
            
            return jsonify({
                'success': True,
                'message': 'Consolidated Excel file generated and saved',
                'file_id': file_id,
                'download_url': f'/api/download-generated/{file_id}',
                'metadata': {
                    'total_tokens_used': total_tokens,
                    'document_count': len(companies_data),
                    'companies': [d['company_name'] for d in companies_data],
                    'model': companies_data[0].get('metadata', {}).get('model', 'N/A')
                },
                'used_template': template_used
            }), 200
        else:
            # Return file directly
            try:
                return send_file(
                    excel_file,
                    as_attachment=True,
                    download_name=excel_file.name,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            finally:
                # Clean up after sending
                import atexit
                def cleanup():
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    if template_temp_path and template_temp_path.parent.exists():
                        shutil.rmtree(template_temp_path.parent, ignore_errors=True)
                atexit.register(cleanup)
    
    except Exception as e:
        # Clean up on error
        if 'template_temp_path' in locals() and template_temp_path and template_temp_path.parent.exists():
            shutil.rmtree(template_temp_path.parent, ignore_errors=True)
        _log.error(f"Error generating consolidated Excel: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/download-generated/<file_id>', methods=['GET'])
def download_generated_file(file_id):
    """
    Download generated Excel/CSV file by ID.
    
    Query Parameters:
    - download: Auto-download file (default: true)
    - preview: Return metadata instead of file (default: false)
    """
    try:
        preview = request.args.get('preview', 'false').lower() == 'true'
        
        # Get file metadata
        file_info = file_manager.get_file(file_id)
        
        if not file_info:
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        # Return metadata if preview requested
        if preview:
            return jsonify({
                'success': True,
                'file_info': {
                    'file_id': file_info['file_id'],
                    'company_name': file_info['company_name'],
                    'file_type': file_info['file_type'],
                    'original_name': file_info['original_name'],
                    'created_at': file_info['created_at'],
                    'file_size': file_info['file_size'],
                    'download_count': file_info['download_count']
                }
            }), 200
        
        # Return file
        # Handle missing stored_path (legacy files or corrupted metadata)
        if file_info.get('stored_path'):
            file_path = Path(file_info['stored_path'])
        else:
            # Fallback: reconstruct path from file_id
            extension = '.xlsx' if file_info['file_type'] == 'excel' else '.csv'
            file_path = EXCEL_STORAGE_FOLDER / f"{file_info['file_id']}{extension}"
        
        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': 'File not found on disk'
            }), 404
        
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' \
                   if file_info['file_type'] == 'excel' else 'text/csv'
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_info['original_name'],
            mimetype=mimetype
        )
        
    except Exception as e:
        _log.error(f"Error downloading file: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/list-generated-files', methods=['GET'])
def list_generated_files():
    """
    List all generated files with optional filtering.
    
    Query Parameters:
    - company_name: Filter by company name (optional)
    """
    try:
        company_name = request.args.get('company_name')
        
        files = file_manager.list_files(company_name=company_name)
        
        # Remove stored_path from response for security
        # for file_info in files:
            # file_info.pop('stored_path', None)
        
        return jsonify({
            'success': True,
            'count': len(files),
            'files': files
        }), 200
        
    except Exception as e:
        _log.error(f"Error listing files: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/delete-generated/<file_id>', methods=['DELETE'])
def delete_generated_file(file_id):
    """Delete generated file by ID."""
    try:
        success = file_manager.delete_file(file_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'File deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
    except Exception as e:
        _log.error(f"Error deleting file: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024)}MB'
    }), 413


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    _log.info(f"Starting Flask API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
