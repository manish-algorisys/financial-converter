"""
Streamlit UI for Financial Document Parser
"""
import streamlit as st
import requests
import json
from pathlib import Path
import pandas as pd
from io import BytesIO
from pypdf import PdfReader
import re

# Configuration
API_URL = "http://localhost:5000"
OUTPUT_FOLDER = Path('output')

# Page configuration
st.set_page_config(
    page_title="Financial Document Parser",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'parsed_data' not in st.session_state:
    st.session_state.parsed_data = None
if 'output_files' not in st.session_state:
    st.session_state.output_files = {}
if 'document_name' not in st.session_state:
    st.session_state.document_name = None
if 'save_message' not in st.session_state:
    st.session_state.save_message = None
if 'save_message_type' not in st.session_state:
    st.session_state.save_message_type = None
if 'table_info' not in st.session_state:
    st.session_state.table_info = {}
if 'excel_file_id' not in st.session_state:
    st.session_state.excel_file_id = None
if 'csv_file_id' not in st.session_state:
    st.session_state.csv_file_id = None
if 'generated_files' not in st.session_state:
    st.session_state.generated_files = []
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = []
if 'batch_mode' not in st.session_state:
    st.session_state.batch_mode = False


def check_api_health():
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_supported_companies():
    """Get list of supported companies from API."""
    try:
        response = requests.get(f"{API_URL}/api/companies", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('companies', [])
        return []
    except:
        return []


def scan_folder_for_pdfs(folder_path):
    """Scan folder for PDF files."""
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


def detect_company_name(pdf_file, supported_companies):
    """
    Detect company name from PDF file content.
    
    Args:
        pdf_file: File object or Path to PDF file
        supported_companies: List of supported company names
    
    Returns:
        Detected company name or None if not found
    """
    try:
        # Create company name variations for matching
        company_patterns = {
            'BRITANNIA': [r'britannia', r'britannia\s+industries'],
            'COLGATE': [r'colgate', r'colgate-palmolive', r'colgate\s+palmolive'],
            'DABUR': [r'dabur', r'dabur\s+india'],
            'HUL': [r'hindustan\s+unilever', r'hul', r'unilever'],
            'ITC': [r'\bitc\b', r'itc\s+limited', r'i\.t\.c'],
            'NESTLE': [r'nestle', r'nestlé', r'nestle\s+india'],
            'P&G': [r'procter\s+&\s+gamble', r'procter\s+and\s+gamble', r'p&g', r'p\s+&\s+g'],
        }
        
        # Read PDF content
        try:
            if isinstance(pdf_file, Path):
                reader = PdfReader(str(pdf_file))
            else:
                # File upload object
                reader = PdfReader(pdf_file)
        except Exception as pdf_error:
            st.warning(f"Cannot read PDF (corrupted or invalid): {str(pdf_error)}")
            return None
        
        # Extract text from first few pages (company name usually in header/title)
        text = ""
        for page_num in range(min(3, len(reader.pages))):
            try:
                text += reader.pages[page_num].extract_text() or ""
            except Exception as page_error:
                # Skip pages that cannot be read
                continue
        
        # Reset file pointer for subsequent operations (important for uploaded files)
        if hasattr(pdf_file, 'seek'):
            try:
                pdf_file.seek(0)
            except Exception:
                pass  # Some file objects may not support seek
        
        text_lower = text.lower()
        
        # Try to match company patterns
        for company, patterns in company_patterns.items():
            if company in supported_companies:
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        return company
        
        return None
    except Exception as e:
        st.warning(f"Could not auto-detect company name: {str(e)}")
        return None


def parse_document(file, company_name, prefer_standalone=True, use_fuzzy_matching=True):
    """Send document to API for parsing with optimization options."""
    try:
        files = {'file': (file.name, file, 'application/pdf')}
        data = {
            'company_name': company_name,
            'prefer_standalone': str(prefer_standalone).lower(),
            'use_fuzzy_matching': str(use_fuzzy_matching).lower()
        }
        
        with st.spinner('Processing document... This may take a few minutes.'):
            response = requests.post(
                f"{API_URL}/api/parse",
                files=files,
                data=data,
                timeout=300  # 5 minutes timeout
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            return {
                'success': False,
                'error': error_data.get('error', 'Unknown error occurred')
            }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'Request timeout. The document may be too large or complex.'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error connecting to API: {str(e)}'
        }


def update_financial_data(company_name, document_name, financial_data, create_new=False):
    """Update financial data via API."""
    try:
        payload = {
            'company_name': company_name,
            'document_name': document_name,
            'financial_data': financial_data,
            'create_new': create_new
        }
        
        response = requests.post(
            f"{API_URL}/api/update-financial-data",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            return {
                'success': False,
                'error': error_data.get('error', 'Unknown error occurred')
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error updating data: {str(e)}'
        }


def generate_excel(data, save_to_storage=False):
    """Generate Excel file from financial data."""
    try:
        payload = {
            'company_name': data.get('company_name'),
            'financial_data': data.get('financial_data'),
            'save': save_to_storage
        }
        
        response = requests.post(
            f"{API_URL}/api/generate-excel",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            if save_to_storage:
                return response.json()
            else:
                return {
                    'success': True,
                    'content': response.content,
                    'filename': f"{data.get('company_name', 'Financial')}_Statement.xlsx"
                }
        else:
            try:
                error_data = response.json()
                return {
                    'success': False,
                    'error': error_data.get('error', 'Unknown error occurred')
                }
            except:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text[:200]}'
                }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': 'Cannot connect to Excel API. Make sure the server is running on port 5000.'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error generating Excel: {str(e)}'
        }


def generate_csv(data, save_to_storage=False):
    """Generate CSV file from financial data."""
    try:
        payload = {
            'company_name': data.get('company_name'),
            'financial_data': data.get('financial_data'),
            'save': save_to_storage
        }
        
        response = requests.post(
            f"{API_URL}/api/generate-csv",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            if save_to_storage:
                return response.json()
            else:
                return {
                    'success': True,
                    'content': response.content,
                    'filename': f"{data.get('company_name', 'Financial')}_Statement.csv"
                }
        else:
            try:
                error_data = response.json()
                return {
                    'success': False,
                    'error': error_data.get('error', 'Unknown error occurred')
                }
            except:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text[:200]}'
                }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': 'Cannot connect to Excel API. Make sure the server is running on port 5000.'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error generating CSV: {str(e)}'
        }


def list_generated_files(company_name=None):
    """List generated Excel/CSV files."""
    try:
        params = {'company_name': company_name} if company_name else {}
        response = requests.get(
            f"{API_URL}/api/list-generated-files",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                'success': False,
                'error': 'Unable to fetch file list'
            }
    except:
        return {
            'success': False,
            'error': 'Cannot connect to Excel API'
        }


def generate_excel_ai(company_name, document_name, preferred_format='html', save_to_storage=False, template_excel_file=None):
    """Generate Excel using AI extraction from previously parsed results."""
    try:
        if template_excel_file:
            # Multipart request with Excel template
            files = {
                'template_excel': (template_excel_file.name, template_excel_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            form_data = {
                'company_name': company_name,
                'document_name': document_name,
                'preferred_format': preferred_format,
                'save': str(save_to_storage).lower()
            }
            
            response = requests.post(
                f"{API_URL}/api/generate-excel-ai",
                files=files,
                data=form_data,
                timeout=120
            )
        else:
            # Standard JSON request
            payload = {
                'company_name': company_name,
                'document_name': document_name,
                'preferred_format': preferred_format,
                'save': save_to_storage
            }
            
            response = requests.post(
                f"{API_URL}/api/generate-excel-ai",
                json=payload,
                timeout=120  # Longer timeout for AI processing
            )
        
        if response.status_code == 200:
            if save_to_storage:
                return response.json()
            else:
                # Return file content for download
                return {
                    'success': True,
                    'file_content': response.content,
                    'filename': f"{company_name}_AI_financial_statement.xlsx"
                }
        else:
            error_data = response.json()
            return {
                'success': False,
                'error': error_data.get('error', 'Unknown error')
            }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': 'Cannot connect to AI API. Make sure the server is running and OPENAI_API_KEY is set.'
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'AI extraction timeout. The document may be too complex.'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error generating AI Excel: {str(e)}'
        }

def display_financial_data(data):
    """Display financial data in a formatted table."""
    if not data or 'financial_data' not in data:
        st.warning("No financial data available.")
        return
    
    # Create DataFrame from financial data
    rows = []
    for item in data['financial_data']:
        row = {'Particular': item['particular']}
        row.update(item['values'])
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Display as table
    st.dataframe(df, use_container_width=True, hide_index=True)


def display_editable_financial_data(data, document_name):
    """Display financial data in an editable format."""
    if not data or 'financial_data' not in data:
        st.warning("No financial data available.")
        return
    
    st.info("💡 Review and edit the extracted data below. Click 'Save Changes' when done.")
    
    # Create DataFrame from financial data with keys
    rows = []
    for item in data['financial_data']:
        row = {
            'Key': item['key'],
            'Particular': item['particular']
        }
        row.update(item['values'])
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Display editable data editor
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",  # Allow adding/removing rows
        column_config={
            "Key": st.column_config.TextColumn(
                "Key",
                help="Unique identifier for this financial metric",
                width="medium",
            ),
            "Particular": st.column_config.TextColumn(
                "Particular",
                help="Description of the financial metric",
                width="large",
            ),
        }
    )
    
    # Display any saved messages from previous action
    if st.session_state.save_message:
        if st.session_state.save_message_type == 'success':
            st.success(st.session_state.save_message)
        elif st.session_state.save_message_type == 'error':
            st.error(st.session_state.save_message)
        # Clear the message after displaying
        st.session_state.save_message = None
        st.session_state.save_message_type = None
    
    # Save buttons
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.button("💾 Save Changes", type="primary", use_container_width=True):
            with st.spinner('Saving changes...'):
                # Convert edited DataFrame back to financial_data format
                updated_financial_data = []
                
                for _, row in edited_df.iterrows():
                    # Extract key and particular
                    key = row.get('Key', '')
                    particular = row.get('Particular', '')
                    
                    # Extract all value columns (everything except Key and Particular)
                    values = {}
                    for col in edited_df.columns:
                        if col not in ['Key', 'Particular']:
                            values[col] = row[col]
                    
                    updated_financial_data.append({
                        'key': key,
                        'particular': particular,
                        'values': values
                    })
                
                # Update via API
                result = update_financial_data(
                    company_name=data['company_name'],
                    document_name=document_name,
                    financial_data=updated_financial_data,
                    create_new=False
                )
                
                if result.get('success'):
                    # Store message in session state
                    st.session_state.save_message = "✅ Changes saved successfully!"
                    st.session_state.save_message_type = 'success'
                    # Update session state
                    st.session_state.parsed_data['financial_data'] = updated_financial_data
                    st.rerun()
                else:
                    # Store error message in session state
                    st.session_state.save_message = f"❌ Error saving changes: {result.get('error')}"
                    st.session_state.save_message_type = 'error'
                    st.rerun()
    
    with col2:
        if st.button("📄 Save as New", use_container_width=True):
            with st.spinner('Saving new version...'):
                # Convert edited DataFrame back to financial_data format
                updated_financial_data = []
                
                for _, row in edited_df.iterrows():
                    key = row.get('Key', '')
                    particular = row.get('Particular', '')
                    
                    values = {}
                    for col in edited_df.columns:
                        if col not in ['Key', 'Particular']:
                            values[col] = row[col]
                    
                    updated_financial_data.append({
                        'key': key,
                        'particular': particular,
                        'values': values
                    })
                
                # Update via API (create new file)
                result = update_financial_data(
                    company_name=data['company_name'],
                    document_name=document_name,
                    financial_data=updated_financial_data,
                    create_new=True
                )
                
                if result.get('success'):
                    # Store success message in session state
                    file_name = Path(result.get('file_path', '')).name
                    st.session_state.save_message = f"✅ New version saved successfully! File: {file_name}"
                    st.session_state.save_message_type = 'success'
                    st.rerun()
                else:
                    # Store error message in session state
                    st.session_state.save_message = f"❌ Error saving new version: {result.get('error')}"
                    st.session_state.save_message_type = 'error'
                    st.rerun()
    
    # Show comparison if there are changes
    if not df.equals(edited_df):
        with st.expander("🔍 View Changes"):
            st.write("**Original Data:**")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.write("**Modified Data:**")
            st.dataframe(edited_df, use_container_width=True, hide_index=True)


def main():
    # Header
    st.markdown('<div class="main-header">📊 Financial Document Parser</div>', unsafe_allow_html=True)
    
    # Check API health
    api_status = check_api_health()
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.info("""
        This tool extracts financial data from quarterly reports (PDF) 
        and converts them into structured JSON, Excel, and CSV formats.
        
        **✨ v2.3 Features (NEW):**
        - 📊 Column Mapping Templates
        - 🎯 Auto-detect company name
        - 🔤 Fuzzy metric matching
        - 📋 No syntax required!
        
        **v2.2 Features:**
        - 📊 Professional Excel export
        - 📄 CSV generation
        - 🔢 Indian number formatting
        - 💾 File management
        
        **v2.1 Features:**
        - 🤖 AI-powered extraction
        - 📋 Custom Excel templates
        - 🔄 Dual-mode filling
        
        **v2.0 Features:**
        - 🔄 Multi-format PDF support
        - 🎯 Smart page detection
        - 📊 Intelligent table selection
        - 🔍 Fuzzy label matching
        
        **Supported Companies:**
        - Britannia, Colgate, Dabur
        - HUL, ITC, Nestlé, P&G
        """)
        
        st.divider()
        
        st.header("API Status")
        if api_status:
            st.success("✅ API is running")
        else:
            st.error("❌ Parser API (Port 5000)")
            st.warning("Start: `python app.py`")
        
        # Check Excel API status
        try:
            excel_response = requests.get(f"{API_URL}/health", timeout=2)
            excel_status = excel_response.status_code == 200
        except:
            excel_status = False
    
    # Main content
    if not api_status:
        st.error("⚠️ Cannot connect to API server. Please ensure the Flask API is running.")
        st.code("python app.py", language="bash")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📤 Upload & Parse", 
        "✏️ Review & Edit", 
        "📊 View Results", 
        "🤖 AI Excel Generator",
        "📁 Saved Files"
    ])
    
    with tab1:
        st.header("Upload Financial Document(s)")
        
        # Get supported companies
        companies = get_supported_companies()
        
        if not companies:
            st.error("Unable to fetch supported companies from API.")
            return
        
        # Upload mode selection
        upload_mode = st.radio(
            "Select Upload Mode:",
            options=["Single File", "Multiple Files", "Folder Path"],
            horizontal=True,
            help="Choose how you want to provide PDF files for parsing"
        )
        
        # Initialize company selection state
        if 'detected_company' not in st.session_state:
            st.session_state.detected_company = None
        if 'manual_override' not in st.session_state:
            st.session_state.manual_override = False
        
        # Advanced options in expander
        with st.expander("⚙️ Advanced Options (v2.0 Optimizations)"):
            col_opt1, col_opt2 = st.columns(2)
            
            with col_opt1:
                prefer_standalone = st.checkbox(
                    "Prefer Standalone Statements",
                    value=True,
                    help="Prioritize standalone over consolidated financial statements"
                )
            
            with col_opt2:
                use_fuzzy_matching = st.checkbox(
                    "Enable Fuzzy Matching",
                    value=True,
                    help="Use fuzzy label matching as fallback when row numbers don't match"
                )
            
            st.info("""
            **💡 Tips:**
            - **Prefer Standalone**: Keep enabled to find standalone statements first
            - **Fuzzy Matching**: Keep enabled for better handling of PDF format variations
            - Both options are recommended for most cases
            """)
        
        # File input based on mode
        uploaded_files = []
        folder_path = None
        
        if upload_mode == "Single File":
            uploaded_file = st.file_uploader(
                "Choose a PDF file",
                type=['pdf'],
                help="Upload a quarterly financial report in PDF format"
            )
            if uploaded_file:
                print(f"Uploaded file: {uploaded_file}")
                uploaded_files = [uploaded_file]
                
                # Auto-detect company name
                if not st.session_state.manual_override:
                    detected = detect_company_name(uploaded_file, companies)
                    if detected:
                        st.session_state.detected_company = detected
                        st.success(f"🔍 Auto-detected company: **{detected}**")
                    else:
                        st.warning("⚠️ Could not auto-detect company. Please select manually.")
        
        elif upload_mode == "Multiple Files":
            uploaded_files_temp = st.file_uploader(
                "Choose PDF files",
                type=['pdf'],
                accept_multiple_files=True,
                help="Upload multiple quarterly financial reports in PDF format"
            )
            if uploaded_files_temp:
                uploaded_files = uploaded_files_temp
                st.info(f"📄 {len(uploaded_files)} files uploaded. Company names will be auto-detected for each file.")
        
        else:  # Folder Path
            folder_path = st.text_input(
                "Enter folder path containing PDF files:",
                placeholder="e.g., D:/financial_reports/Q2_2025",
                help="Provide absolute path to folder containing PDF files"
            )
        
        # Manual company override option (only for single file mode)
        if upload_mode == "Single File" and uploaded_files:
            with st.expander("🔧 Manual Company Selection (Override Auto-detection)"):
                manual_company = st.selectbox(
                    "Select Company Manually",
                    options=["Auto-detect"] + companies,
                    index=0 if not st.session_state.manual_override else (companies.index(st.session_state.detected_company) + 1 if st.session_state.detected_company in companies else 0),
                    help="Override auto-detection and manually select the company"
                )
                
                if manual_company != "Auto-detect":
                    st.session_state.detected_company = manual_company
                    st.session_state.manual_override = True
                else:
                    st.session_state.manual_override = False
        
        # Process based on mode
        if upload_mode == "Folder Path" and folder_path:
            st.info(f"📁 **Folder:** {folder_path}")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("🔍 Scan & Parse Folder", type="primary", use_container_width=True):
                    # Scan folder
                    scan_result = scan_folder_for_pdfs(folder_path)
                    
                    if not scan_result['success']:
                        st.error(f"❌ {scan_result['error']}")
                    else:
                        pdf_files = scan_result['files']
                        st.info(f"Found {scan_result['count']} PDF file(s)")
                        
                        # Process all PDFs
                        st.session_state.batch_results = []
                        st.session_state.batch_mode = True
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, pdf_path in enumerate(pdf_files):
                            status_text.text(f"Processing {idx + 1}/{len(pdf_files)}: {pdf_path.name}")
                            
                            # Auto-detect company name for this PDF
                            detected_company = detect_company_name(pdf_path, companies)
                            
                            if not detected_company:
                                # Skip this file if company cannot be detected
                                result = {
                                    'success': False,
                                    'error': 'Could not auto-detect company name',
                                    'filename': pdf_path.name
                                }
                                st.session_state.batch_results.append(result)
                                progress_bar.progress((idx + 1) / len(pdf_files))
                                continue
                            
                            with open(pdf_path, 'rb') as f:
                                result = parse_document(
                                    f,
                                    detected_company,
                                    prefer_standalone=prefer_standalone,
                                    use_fuzzy_matching=use_fuzzy_matching
                                )
                                
                                result['filename'] = pdf_path.name
                                result['detected_company'] = detected_company
                                st.session_state.batch_results.append(result)
                            
                            progress_bar.progress((idx + 1) / len(pdf_files))
                        
                        status_text.text(f"✅ Completed processing {len(pdf_files)} files")
                        st.rerun()
            
            with col2:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.batch_results = []
                    st.session_state.batch_mode = False
                    st.session_state.parsed_data = None
                    st.session_state.output_files = {}
                    st.session_state.detected_company = None
                    st.session_state.manual_override = False
                    st.rerun()
        
        elif uploaded_files:
            # Display file info
            if len(uploaded_files) == 1:
                st.info(f"📄 **File:** {uploaded_files[0].name} ({uploaded_files[0].size / 1024:.2f} KB)")
            else:
                total_size = sum(f.size for f in uploaded_files) / 1024
                st.info(f"📄 **Files:** {len(uploaded_files)} PDFs ({total_size:.2f} KB total)")
                with st.expander("View files"):
                    for f in uploaded_files:
                        st.text(f"• {f.name} ({f.size / 1024:.2f} KB)")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("🚀 Parse Document(s)", type="primary", use_container_width=True):
                    if len(uploaded_files) == 1:
                        # Single file mode - use detected or manually selected company
                        company_to_use = st.session_state.detected_company
                        
                        result = parse_document(
                            uploaded_files[0], 
                            company_to_use,
                            prefer_standalone=prefer_standalone,
                            use_fuzzy_matching=use_fuzzy_matching
                        )
                        print(result, "--- result")
                            
                        if result.get('success'):
                            st.session_state.parsed_data = result.get('data')
                            st.session_state.output_files = result.get('output_files', {})
                            st.session_state.processing_time = result.get('processing_time')
                            st.session_state.table_info = result.get('table_info', {})
                            st.session_state.document_name = Path(uploaded_files[0].name).stem
                            st.session_state.batch_mode = False
                            st.rerun()
                        else:
                            st.error(f"❌ {result.get('error', 'Unknown error')}")
                    else:
                        # Batch mode - auto-detect company for each file
                        st.session_state.batch_results = []
                        st.session_state.batch_mode = True
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, uploaded_file in enumerate(uploaded_files):
                            status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                            
                            # Auto-detect company for this file
                            detected_company = detect_company_name(uploaded_file, companies)
                            print(detected_company, "---- detected_company")
                            
                            if not detected_company:
                                # Skip this file if company cannot be detected
                                result = {
                                    'success': False,
                                    'error': 'Could not auto-detect company name',
                                    'filename': uploaded_file.name
                                }
                                st.session_state.batch_results.append(result)
                                progress_bar.progress((idx + 1) / len(uploaded_files))
                                continue

                            print("Parsing document...", uploaded_file)
                            
                            result = parse_document(
                                uploaded_file,
                                detected_company,
                                prefer_standalone=prefer_standalone,
                                use_fuzzy_matching=use_fuzzy_matching
                            )
                            
                            result['filename'] = uploaded_file.name
                            result['detected_company'] = detected_company
                            st.session_state.batch_results.append(result)
                            
                            progress_bar.progress((idx + 1) / len(uploaded_files))
                        
                        status_text.text(f"✅ Completed processing {len(uploaded_files)} files")
                        st.rerun()
            
            with col2:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.parsed_data = None
                    st.session_state.output_files = {}
                    st.session_state.table_info = {}
                    st.session_state.save_message = None
                    st.session_state.save_message_type = None
                    st.session_state.batch_results = []
                    st.session_state.batch_mode = False
                    st.session_state.detected_company = None
                    st.session_state.manual_override = False
                    st.rerun()
        
        # Display results
        if st.session_state.batch_mode and st.session_state.batch_results:
            st.divider()
            st.success(f"✅ Processed {len(st.session_state.batch_results)} document(s)!")
            
            # Summary statistics
            successful = sum(1 for r in st.session_state.batch_results if r.get('success'))
            failed = len(st.session_state.batch_results) - successful
            
            col_sum1, col_sum2, col_sum3 = st.columns(3)
            with col_sum1:
                st.metric("Total Files", len(st.session_state.batch_results))
            with col_sum2:
                st.metric("Successful", successful)
            with col_sum3:
                st.metric("Failed", failed)
            
            # Display results for each file
            st.subheader("Processing Results")
            for idx, result in enumerate(st.session_state.batch_results, 1):
                filename = result.get('filename', f'File {idx}')
                detected_company = result.get('detected_company', 'Unknown')
                print(f"result: => {result}")
                
                with st.expander(f"{'✅' if result.get('success') else '❌'} {filename} - {detected_company}", expanded=False):
                    if result.get('success'):
                        data = result.get('data', {})
                        
                        col_info1, col_info2, col_info3, col_info4 = st.columns(4)
                        with col_info1:
                            st.metric("Detected Company", detected_company)
                        with col_info2:
                            st.metric("Company", data.get('company_name', 'N/A'))
                        with col_info3:
                            st.metric("Items Extracted", len(data.get('financial_data', [])))
                        with col_info4:
                            st.metric("Processing Time", f"{result.get('processing_time', 0)[0]:.1f}s")
                        
                        # Show table info
                        table_info = result.get('table_info', {})
                        if table_info:
                            st.info(f"""
                            **Table Selection:** {table_info.get('total_tables', 0)} table(s) found, 
                            selected table #{table_info.get('selected_table', 'N/A')} 
                            using {table_info.get('selection_method', 'unknown')} method
                            """)
                        
                        # Preview data
                        if st.checkbox(f"Preview data - {filename}", key=f"preview_{idx}"):
                            display_financial_data(data)
                    else:
                        st.error(f"Error: {result.get('error', 'Unknown error')}")
        
        elif st.session_state.parsed_data:
            st.divider()
            st.success("✅ Document parsed successfully!")
            
            # Display processing info
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                if st.session_state.get('processing_time'):
                    processing_time = st.session_state.processing_time
                    if isinstance(processing_time, (int, float)):
                        st.metric("⏱️ Processing Time", f"{processing_time:.2f}s")
                    else:
                        st.metric("⏱️ Processing Time", str(processing_time))
            
            with col_info2:
                # Display table info if available
                table_info = st.session_state.get('table_info', {})
                if table_info:
                    total_tables = table_info.get('total_tables', 0)
                    selected_table = table_info.get('selected_table', 1)
                    st.metric("📊 Tables Found", f"{selected_table}/{total_tables}")
            
            with col_info3:
                # Display extraction method from metadata
                metadata = st.session_state.parsed_data.get('metadata', {})
                if metadata:
                    extraction_method = metadata.get('extraction_method', 'N/A')
                    method_emoji = "🎯" if extraction_method == "tr_number" else "🔄" if extraction_method == "mixed" else "🔍"
                    st.metric(f"{method_emoji} Extraction", extraction_method.title())
            
            # Display table selection details if multiple tables
            table_info = st.session_state.get('table_info', {})
            if table_info.get('total_tables', 0) > 1:
                with st.expander("ℹ️ Table Selection Details"):
                    st.write(f"**Total tables found:** {table_info.get('total_tables')}")
                    st.write(f"**Selected table:** {table_info.get('selected_table')}")
                    st.write(f"**Selection method:** {table_info.get('selection_method')}")
                    
                    selection_method = table_info.get('selection_method')
                    if selection_method == 'heuristic':
                        st.info("💡 The best table was automatically selected using content analysis (financial keywords, row count, numeric data).")
                    elif selection_method == 'single_table':
                        st.info("💡 Only one table was found in the document.")
                    elif selection_method == 'default':
                        st.info("💡 The first table was used as default.")
            
            # Display metadata if available
            metadata = st.session_state.parsed_data.get('metadata', {})
            if metadata and len(metadata) > 2:  # More than just basic metadata
                with st.expander("📋 Extraction Metadata"):
                    col_meta1, col_meta2 = st.columns(2)
                    
                    with col_meta1:
                        st.write(f"**Source file:** {metadata.get('source_file', 'N/A')}")
                        st.write(f"**Table number:** {metadata.get('table_number', 'N/A')}")
                        st.write(f"**Total tables:** {metadata.get('total_tables', 'N/A')}")
                    
                    with col_meta2:
                        st.write(f"**Extraction method:** {metadata.get('extraction_method', 'N/A')}")
                        processing_time = metadata.get('processing_time_seconds', 'N/A')
                        if isinstance(processing_time, (int, float)):
                            st.write(f"**Processing time:** {processing_time:.2f}s")
                        else:
                            st.write(f"**Processing time:** {processing_time}")
                    
                    # Explain extraction method
                    extraction_method = metadata.get('extraction_method', '')
                    if extraction_method == 'tr_number':
                        st.success("✅ All data extracted using configured row numbers (most accurate)")
                    elif extraction_method == 'mixed':
                        st.warning("⚠️ Some data extracted using fuzzy label matching - PDF format may differ from configuration")
                    elif extraction_method == 'fuzzy':
                        st.info("ℹ️ Data extracted primarily using fuzzy label matching - consider updating configuration for this PDF format")
            
            st.subheader("Extracted Financial Data (Preview)")
            display_financial_data(st.session_state.parsed_data)
            
            st.info("💡 Switch to the '✏️ Review & Edit' tab to review and modify the extracted data.")
            
            # Download options
            st.divider()
            st.subheader("📥 Download Results")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Download JSON
                json_str = json.dumps(st.session_state.parsed_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📄 JSON",
                    data=json_str,
                    file_name=f"{st.session_state.parsed_data['company_name']}_financial_data.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col2:
                # Download CSV (if available)
                if 'csv_1' in st.session_state.output_files:
                    csv_path = st.session_state.output_files['csv_1']
                    try:
                        with open(csv_path, 'r', encoding='utf-8') as f:
                            csv_data = f.read()
                        st.download_button(
                            label="📊 Table CSV",
                            data=csv_data,
                            file_name=Path(csv_path).name,
                            mime="text/csv",
                            use_container_width=True
                        )
                    except:
                        st.button("📊 Table CSV", disabled=True, use_container_width=True)
            
            with col3:
                # Download Markdown (if available)
                if 'md_1' in st.session_state.output_files:
                    md_path = st.session_state.output_files['md_1']
                    try:
                        with open(md_path, 'r', encoding='utf-8') as f:
                            md_data = f.read()
                        st.download_button(
                            label="📝 Markdown",
                            data=md_data,
                            file_name=Path(md_path).name,
                            mime="text/markdown",
                            use_container_width=True
                        )
                    except:
                        st.button("📝 Markdown", disabled=True, use_container_width=True)
            
            with col4:
                # Download HTML (if available)
                if 'html_1' in st.session_state.output_files:
                    html_path = st.session_state.output_files['html_1']
                    try:
                        with open(html_path, 'r', encoding='utf-8') as f:
                            html_data = f.read()
                        st.download_button(
                            label="🌐 HTML",
                            data=html_data,
                            file_name=Path(html_path).name,
                            mime="text/html",
                            use_container_width=True
                        )
                    except:
                        st.button("🌐 HTML", disabled=True, use_container_width=True)
            
            # Excel/CSV Generation Section (NEW)
            st.divider()
            st.subheader("📊 Generate Financial Statement")
            
            # Check if Excel API is available
            try:
                excel_response = requests.get(f"{API_URL}/health", timeout=2)
                excel_api_available = excel_response.status_code == 200
            except:
                excel_api_available = False
            
            if excel_api_available:
                st.info("💡 Generate professionally formatted 47-row financial statements with Indian number formatting")
                
                # Save option
                save_to_storage = st.checkbox(
                    "💾 Save to storage (track in Saved Files tab)",
                    value=False,
                    help="Save generated files for later access and tracking"
                )
                
                col_excel1, col_excel2, col_excel3 = st.columns(3)
                
                with col_excel1:
                    if st.button("📊 Generate Excel", type="primary", use_container_width=True):
                        with st.spinner('Generating Excel file...'):
                            result = generate_excel(st.session_state.parsed_data, save_to_storage=save_to_storage)
                            
                            if result.get('success'):
                                if save_to_storage:
                                    # File was saved, now download it
                                    file_id = result.get('file_id')
                                    download_url = f"{API_URL}/api/download-generated/{file_id}"
                                    
                                    try:
                                        download_response = requests.get(download_url, timeout=10)
                                        if download_response.status_code == 200:
                                            company = st.session_state.parsed_data.get('company_name', 'Financial')
                                            st.download_button(
                                                label="⬇️ Download Excel",
                                                data=download_response.content,
                                                file_name=f"{company}_Statement.xlsx",
                                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                                use_container_width=True
                                            )
                                            st.success(f"✅ Excel saved & ready! File ID: {file_id[:8]}...")
                                            st.info("📁 View in 'Saved Files' tab")
                                        else:
                                            st.error("❌ Failed to download saved file")
                                    except Exception as e:
                                        st.error(f"❌ Download error: {str(e)}")
                                else:
                                    # Direct download
                                    st.download_button(
                                        label="⬇️ Download Excel",
                                        data=result['content'],
                                        file_name=result['filename'],
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True
                                    )
                                    st.success("✅ Excel generated!")
                            else:
                                st.error(f"❌ {result.get('error')}")
                
                with col_excel2:
                    if st.button("📄 Generate CSV", use_container_width=True):
                        with st.spinner('Generating CSV file...'):
                            result = generate_csv(st.session_state.parsed_data, save_to_storage=save_to_storage)
                            
                            if result.get('success'):
                                if save_to_storage:
                                    # File was saved, now download it
                                    file_id = result.get('file_id')
                                    download_url = f"{API_URL}/api/download-generated/{file_id}"
                                    
                                    try:
                                        download_response = requests.get(download_url, timeout=10)
                                        if download_response.status_code == 200:
                                            company = st.session_state.parsed_data.get('company_name', 'Financial')
                                            st.download_button(
                                                label="⬇️ Download CSV",
                                                data=download_response.content,
                                                file_name=f"{company}_Statement.csv",
                                                mime="text/csv",
                                                use_container_width=True
                                            )
                                            st.success(f"✅ CSV saved & ready! File ID: {file_id[:8]}...")
                                            st.info("📁 View in 'Saved Files' tab")
                                        else:
                                            st.error("❌ Failed to download saved file")
                                    except Exception as e:
                                        st.error(f"❌ Download error: {str(e)}")
                                else:
                                    # Direct download
                                    st.download_button(
                                        label="⬇️ Download CSV",
                                        data=result['content'],
                                        file_name=result['filename'],
                                        mime="text/csv",
                                        use_container_width=True
                                    )
                                    st.success("✅ CSV generated!")
                            else:
                                st.error(f"❌ {result.get('error')}")
                
                with col_excel3:
                    with st.popover("ℹ️ About Format", use_container_width=True):
                        st.markdown("""
                        **Excel/CSV Format:**
                        - 47 rows × 12 columns
                        - 11 financial periods
                        - Indian number formatting
                        - Professional styling (Excel)
                        - Sections: Revenue, Expenses, PBT, Tax, Net Profit, EBITDA, Growth
                        
                        **Features:**
                        - Bold headers with gray background
                        - Borders on all cells
                        - Double underlines for totals
                        - Bracket notation for negatives: (123)
                        """)
            else:
                st.warning("⚠️ Excel/CSV generation is not available. Start the Excel API server on port 5000 to enable this feature.")
                with st.expander("How to enable Excel/CSV generation"):
                    st.code("python app.py", language="bash")
                    st.caption("The Excel API should be running on port 5000")
    
    with tab2:
        st.header("Review & Edit Financial Data")
        
        if st.session_state.parsed_data:
            # Get document name from session state or output files
            document_name = st.session_state.document_name
            
            if not document_name and st.session_state.output_files and 'json' in st.session_state.output_files:
                json_path = Path(st.session_state.output_files['json'])
                # Extract document name from path like: output/COMPANY_DocName/DocName-financial-data.json
                document_name = json_path.parent.name.split('_', 1)[1] if '_' in json_path.parent.name else json_path.stem.replace('-financial-data', '')
            
            if not document_name:
                # Fallback: try to infer from company name
                document_name = st.session_state.parsed_data.get('company_name', 'document')
            
            # Company info
            company_name = st.session_state.parsed_data.get('company_name', 'N/A')
            st.subheader(f"Company: {company_name}")
            st.caption(f"Document: {document_name}")
            
            st.divider()
            
            # Display editable financial data
            display_editable_financial_data(st.session_state.parsed_data, document_name)
            
        else:
            st.info("👈 No results yet. Upload and parse a document in the 'Upload & Parse' tab first.")
    
    with tab3:
        st.header("View Parsing Results")
        
        if st.session_state.parsed_data:
            # Company info
            company_name = st.session_state.parsed_data.get('company_name', 'N/A')
            st.subheader(f"Company: {company_name}")
            
            # Display financial data
            display_financial_data(st.session_state.parsed_data)
            
            # JSON view in expander
            with st.expander("🔍 View Raw JSON"):
                st.json(st.session_state.parsed_data)
            
            # File information
            if st.session_state.output_files:
                with st.expander("📁 Generated Files"):
                    for key, path in st.session_state.output_files.items():
                        st.text(f"{key}: {Path(path).name}")
        else:
            st.info("👈 No results yet. Upload and parse a document in the 'Upload & Parse' tab.")
    
    with tab4:
        st.header("🤖 AI-Powered Excel Generator")
        
        st.info("""
        **✨ Generate Excel files using AI extraction from previously parsed documents.**
        
        This feature uses OpenAI GPT models to intelligently extract financial data from 
        your parsed HTML/Markdown tables and generate professional Excel statements.
        
        **Benefits:**
        - 🧠 Smart extraction handles format variations
        - 🔄 Works with existing parse results (no re-upload needed)
        - 📊 Generates professionally formatted Excel files
        - ⚡ Faster than manual review for standard formats
        """)
        
        # Check if AI API is available
        try:
            health_response = requests.get(f"{API_URL}/health", timeout=2)
            api_available = health_response.status_code == 200
        except:
            api_available = False
        
        if not api_available:
            st.warning("⚠️ AI Excel API is not available. Ensure Flask API is running with OPENAI_API_KEY set.")
            st.code("export OPENAI_API_KEY='your-key-here'\npython app.py", language="bash")
            return
        
        st.divider()
        
        # Input section
        st.subheader("📋 Select Parsed Document")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            ai_company_name = st.selectbox(
                "Company Name",
                options=get_supported_companies(),
                help="Select the company",
                key="ai_company_select"
            )
        
        with col2:
            # List available parsed documents for the company
            if ai_company_name:
                available_docs = []
                output_folder = OUTPUT_FOLDER
                for folder in output_folder.glob(f"{ai_company_name}_*"):
                    if folder.is_dir():
                        doc_name = folder.name.replace(f"{ai_company_name}_", "")
                        available_docs.append(doc_name)
                
                if available_docs:
                    ai_document_name = st.selectbox(
                        "Parsed Document",
                        options=available_docs,
                        help="Select a previously parsed document",
                        key="ai_doc_select"
                    )
                else:
                    st.warning(f"⚠️ No parsed documents found for {ai_company_name}. Parse a document first in the 'Upload & Parse' tab.")
                    ai_document_name = None
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            preferred_format = st.radio(
                "Preferred Source Format",
                options=["html", "markdown"],
                index=0,
                help="Format to use for AI extraction (HTML is generally more structured)"
            )
            
            save_to_storage = st.checkbox(
                "Save to File Storage",
                value=False,
                help="Save generated file for later download (otherwise downloads immediately)"
            )
        
        # Excel Template Upload Section
        with st.expander("📋 Custom Excel Template (v2.3 - NEW: Column Mapping)", expanded=False):
            st.markdown("""
            **✨ NEW: Two ways to customize your Excel output!**
            
            ### 📊 Method 1: Column Mapping (Recommended - No Syntax Required!)
            
            **Simple 3-row structure:**
            ```
            Row 1: [A1: empty] | [B1:E1: MERGED] COMPANY_NAME_PLACEHOLDER
            Row 2: Metric      | 30.06.2025 Q    | 31.03.2025 Q    | 30.06.2024 Q    | 31.03.2025 Y
            Row 3: Sale of Goods
            Row 4: Export Sales
            Row 5: Net Profit
            ...
            ```
            
            **Features:**
            - ✅ No placeholder syntax needed!
            - ✅ Company name auto-filled in merged B1:E1 cells
            - ✅ Headers detected automatically from Row 2
            - ✅ Fuzzy matching for metric names (typo-tolerant)
            - ✅ Professional financial report format
            
            **Supported Period Formats (Row 2 Headers):**
            - `30.06.2025 Q` - Quarterly with date and Q suffix
            - `31.03.2025 Y` - Yearly with date and Y suffix
            - `Q1 FY2026`, `Q2 2025` - Quarter labels
            - `FY 2025`, `Year 2025` - Year labels
            
            **Supported Metric Names (Column A from Row 3):**
            Sale of Goods, Export Sales, Revenue from Operations, Other Income, Total Income,
            Cost of Materials Consumed, Employee Benefits Expense, Finance Costs, 
            Depreciation and Amortisation, Other Expenses, Total Expenses,
            Profit Before Tax, Net Profit, EPS Basic, EPS Diluted, etc.
            
            ---
            
            ### 🔧 Method 2: Placeholder Mode (Advanced - Legacy)
            
            Use `{{key[period]}}` syntax for flexible placement anywhere in your template.
            
            **Placeholder Examples:**
            - `{{company_name}}` - Company name
            - `{{revenue_from_operations[30.06.2025]}}` - Revenue for Q1 FY2026
            - `{{net_profit[31.03.2025_Y]}}` - Net profit for FY2025
            - `{{eps_basic[30.06.2024]}}` - EPS for Q1 FY2025
            
            ---
            
            **System Behavior:**
            1. ✅ Tries Column Mapping first (if Row 2 has period headers)
            2. ✅ Falls back to Placeholder mode (if `{{}}` placeholders found)
            3. ⚠️ Returns template unchanged if neither detected
            
            **Sample Template:** `templates/financial_summary_template_column_mapping.xlsx`
            
            📖 **Full Documentation:** See `COLUMN_MAPPING_GUIDE.md` for detailed instructions
            """)
            
            template_excel_file = st.file_uploader(
                "Upload Excel Template",
                type=['xlsx', 'xls'],
                help="Upload Excel template (supports Column Mapping or Placeholder modes)",
                key="ai_excel_template_uploader"
            )
            
            if template_excel_file:
                st.success(f"✅ Template uploaded: {template_excel_file.name}")
                st.info("💡 System will automatically detect structure (Column Mapping or Placeholder mode) and fill data accordingly.")
                
                # Provide helpful hints
                col_hint1, col_hint2 = st.columns(2)
                with col_hint1:
                    st.caption("**Column Mapping Format:**")
                    st.code("Row 1: Company Name (merged)\nRow 2: Headers\nRow 3+: Metrics", language="text")
                with col_hint2:
                    st.caption("**Placeholder Format:**")
                    st.code("{{key[period]}}\nAnywhere in template", language="text")
                
                template_excel_file.seek(0)  # Reset for later use
            else:
                st.info("💡 Without a template, the default 47-row format will be used")
        
        # Generate button
        if ai_company_name and ai_document_name:
            st.divider()
            
            # Preview source files
            output_dir = OUTPUT_FOLDER / f"{ai_company_name}_{ai_document_name}"
            
            col_preview1, col_preview2 = st.columns(2)
            
            with col_preview1:
                st.caption("📄 Available Source Files:")
                table_files = list(output_dir.glob("*-table-*"))
                for file in table_files:
                    st.text(f"• {file.name}")
            
            with col_preview2:
                st.caption("ℹ️ Extraction Info:")
                st.text(f"Company: {ai_company_name}")
                st.text(f"Document: {ai_document_name}")
                st.text(f"Format: {preferred_format.upper()}")
            
            st.divider()
            
            if st.button("🚀 Generate Excel with AI", type="primary", use_container_width=True):
                with st.spinner('🤖 AI is extracting financial data... This may take 30-60 seconds.'):
                    # Get template file if provided
                    template_file = st.session_state.get('ai_excel_template_uploader')
                    
                    result = generate_excel_ai(
                        ai_company_name, 
                        ai_document_name,
                        preferred_format=preferred_format,
                        save_to_storage=save_to_storage,
                        template_excel_file=template_file
                    )
                
                if result.get('success'):
                    st.success("✅ Excel file generated successfully using AI!")
                    
                    # Show metadata if available
                    if 'metadata' in result:
                        metadata = result['metadata']
                        
                        col_meta1, col_meta2, col_meta3 = st.columns(3)
                        with col_meta1:
                            st.metric("AI Model", metadata.get('model', 'N/A'))
                        with col_meta2:
                            st.metric("Tokens Used", metadata.get('tokens_used', 'N/A'))
                        with col_meta3:
                            st.metric("Source Format", metadata.get('source_format', 'N/A').upper())
                    
                    if save_to_storage:
                        # Show file ID and download link
                        file_id = result.get('file_id')
                        st.info(f"📁 File saved with ID: `{file_id}`")
                        st.markdown(f"**Download URL:** {result.get('download_url')}")
                        
                        # Download button
                        if st.button("📥 Download Now", use_container_width=True):
                            download_url = f"{API_URL}{result.get('download_url')}"
                            st.markdown(f"[Click here to download]({download_url})")
                    else:
                        # Provide download
                        file_content = result.get('file_content')
                        filename = result.get('filename', 'financial_statement.xlsx')
                        
                        st.download_button(
                            label="📥 Download Excel File",
                            data=file_content,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        
                        st.balloons()
                else:
                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                    
                    # Provide helpful suggestions
                    if 'OPENAI_API_KEY' in result.get('error', ''):
                        st.warning("💡 Make sure OPENAI_API_KEY environment variable is set before starting the Flask API.")
                        st.code("export OPENAI_API_KEY='sk-...'", language="bash")
        else:
            st.warning("👆 Please select a company and document to continue.")
    
    with tab5:
        st.header("📁 Saved Excel/CSV Files")
        
        # Check if Excel API is available
        try:
            excel_response = requests.get(f"{API_URL}/health", timeout=2)
            excel_api_available = excel_response.status_code == 200
        except:
            excel_api_available = False
        
        if not excel_api_available:
            st.warning("⚠️ Excel/CSV file management is not available. Start the Excel API server on port 5000.")
            st.code("python app.py", language="bash")
            return
        
        # Refresh and filter options
        col_filter1, col_filter2, col_filter3 = st.columns([2, 1, 1])
        
        with col_filter1:
            company_filter = st.text_input(
                "🔍 Filter by company name",
                placeholder="e.g., BRITANNIA",
                help="Leave empty to show all files"
            )
        
        with col_filter2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        with col_filter3:
            st.write("")  # Spacing
        
        # Fetch files
        with st.spinner('Loading saved files...'):
            result = list_generated_files(company_name=company_filter if company_filter else None)
        
        if result.get('success'):
            files = result.get('files', [])
            
            if files:
                st.success(f"📊 Found {len(files)} file(s)")
                
                # Display files in a grid
                for idx, file_info in enumerate(files):
                    with st.container():
                        col_info, col_actions = st.columns([3, 1])
                        
                        with col_info:
                            file_type_emoji = "📊" if file_info['file_type'] == 'excel' else "📄"
                            st.markdown(f"**{file_type_emoji} {file_info['original_name']}**")
                            
                            col_meta1, col_meta2, col_meta3 = st.columns(3)
                            with col_meta1:
                                st.caption(f"🏢 {file_info['company_name']}")
                            with col_meta2:
                                st.caption(f"📏 {file_info['file_size'] / 1024:.1f} KB")
                            with col_meta3:
                                st.caption(f"⬇️ {file_info['download_count']} downloads")
                            
                            st.caption(f"📅 Created: {file_info['created_at'][:10]}")
                        
                        with col_actions:
                            # Download button - fetch file on demand
                            download_url = f"{API_URL}/api/download-generated/{file_info['file_id']}"
                            
                            # Fetch file data for download button
                            # Streamlit requires data upfront for download_button
                            file_data = None
                            error_msg = None
                            
                            try:
                                download_response = requests.get(download_url, timeout=10)
                                if download_response.status_code == 200:
                                    file_data = download_response.content
                                else:
                                    print(f"Download failed due to error {download_response.text}")
                                    error_msg = f"Status {download_response.status_code}"
                            except requests.exceptions.ConnectionError:
                                error_msg = "API not reachable"
                            except requests.exceptions.Timeout:
                                error_msg = "Request timeout"
                            except Exception as e:
                                error_msg = f"Error: {str(e)[:30]}"

                            print(f"File {file_info['original_name']} download fetch: {'Success' if file_data else 'Failed - ' + error_msg}")
                            
                            # Show download button if file data loaded successfully
                            if file_data:
                                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
                                    if file_info['file_type'] == 'excel' else "text/csv"
                                print(f"Preparing download for {file_info['original_name']} with MIME {mime_type}")
                                
                                st.download_button(
                                    label="⬇️ Download",
                                    data=file_data,
                                    file_name=file_info['original_name'],
                                    mime=mime_type,
                                    use_container_width=True,
                                    key=f"download_{idx}"
                                )
                            else:
                                # Show disabled button with error tooltip
                                st.button(
                                    "⬇️ Download",
                                    disabled=True,
                                    use_container_width=True,
                                    key=f"download_{idx}",
                                    help=f"❌ {error_msg}"
                                )
                            
                            # Delete button
                            if st.button("🗑️ Delete", use_container_width=True, key=f"delete_{idx}"):
                                try:
                                    delete_response = requests.delete(
                                        f"{API_URL}/api/delete-generated/{file_info['file_id']}",
                                        timeout=10
                                    )
                                    if delete_response.status_code == 200:
                                        st.success("✅ File deleted!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to delete file")
                                except:
                                    st.error("❌ Error deleting file")
                        
                        st.divider()
                
                # Summary stats
                with st.expander("📊 Statistics"):
                    total_size = sum(f['file_size'] for f in files) / (1024 * 1024)  # MB
                    total_downloads = sum(f['download_count'] for f in files)
                    excel_count = sum(1 for f in files if f['file_type'] == 'excel')
                    csv_count = sum(1 for f in files if f['file_type'] == 'csv')
                    
                    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                    with col_stat1:
                        st.metric("Total Files", len(files))
                    with col_stat2:
                        st.metric("Total Size", f"{total_size:.2f} MB")
                    with col_stat3:
                        st.metric("Excel Files", excel_count)
                    with col_stat4:
                        st.metric("CSV Files", csv_count)
                    
                    st.metric("Total Downloads", total_downloads)
            else:
                st.info("📭 No saved files found. Generate Excel/CSV files from the 'Upload & Parse' tab.")
        else:
            st.error(f"❌ {result.get('error', 'Failed to load files')}")


if __name__ == "__main__":
    main()
