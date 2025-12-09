"""
Flask API for Financial Document Parser Service
"""
import os
import logging
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import shutil

from parser_core import (
    process_pdf_document,
    load_config,
    get_supported_companies
)
from excel_generator import FinancialExcelGenerator, FileManager

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
    Parse financial document with optimized multi-format support.
    
    Expected form data:
    - file: PDF file (required)
    - company_name: Company name (required, e.g., "BRITANNIA", "COLGATE", etc.)
    - prefer_standalone: Prefer standalone over consolidated statements (optional, default: true)
    - use_fuzzy_matching: Enable fuzzy label matching fallback (optional, default: true)
    
    Returns:
    - success: bool
    - message: str
    - data: Parsed financial data
    - output_files: Generated file paths
    - processing_time: Processing duration
    - table_info: Table selection metadata (total_tables, selected_table, selection_method)
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
        
        # Check if company name is provided
        company_name = request.form.get('company_name', '').upper()
        if not company_name:
            return jsonify({
                'success': False,
                'error': 'Company name not provided'
            }), 400
        
        # Validate company name
        if company_name not in get_supported_companies():
            return jsonify({
                'success': False,
                'error': f'Unsupported company: {company_name}. Supported: {get_supported_companies()}'
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only PDF files are allowed.'
            }), 400
        
        # Get optional optimization parameters
        prefer_standalone = request.form.get('prefer_standalone', 'true').lower() == 'true'
        use_fuzzy_matching = request.form.get('use_fuzzy_matching', 'true').lower() == 'true'
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        temp_dir = Path(tempfile.mkdtemp())
        file_path = temp_dir / filename
        file.save(str(file_path))
        
        _log.info(f"Processing file: {filename} for company: {company_name}")
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
            return jsonify({
                'success': True,
                'message': result['message'],
                'data': result['json_result'],
                'output_files': result['output_files'],
                'processing_time': result.get('processing_time'),
                'table_info': result.get('table_info', {})
            }), 200
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
        print(f"file_info: {file_info}")
        
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
        file_path = Path(file_info['stored_path'])
        
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
