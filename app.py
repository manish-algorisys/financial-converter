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
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

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
    Parse financial document.
    
    Expected form data:
    - file: PDF file
    - company_name: Company name (e.g., "BRITANNIA", "COLGATE", etc.)
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
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        temp_dir = Path(tempfile.mkdtemp())
        file_path = temp_dir / filename
        file.save(str(file_path))
        
        _log.info(f"Processing file: {filename} for company: {company_name}")
        
        # Create output directory for this request
        output_dir = OUTPUT_FOLDER / f"{company_name}_{file_path.stem}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process document
        result = process_pdf_document(
            pdf_path=file_path,
            company_name=company_name,
            output_dir=output_dir,
            config=config
        )
        
        # Clean up temporary file
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'data': result['json_result'],
                'output_files': result['output_files'],
                'processing_time': result.get('processing_time')
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
