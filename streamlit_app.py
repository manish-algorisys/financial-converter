"""
Streamlit UI for Financial Document Parser
"""
import streamlit as st
import requests
import json
from pathlib import Path
import pandas as pd
from io import BytesIO

# Configuration
API_URL = "http://localhost:5000"

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


def parse_document(file, company_name):
    """Send document to API for parsing."""
    try:
        files = {'file': (file.name, file, 'application/pdf')}
        data = {'company_name': company_name}
        
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
    
    # Save buttons
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.button("💾 Save Changes", type="primary", use_container_width=True):
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
                st.success("✅ Changes saved successfully!")
                # Update session state
                st.session_state.parsed_data['financial_data'] = updated_financial_data
                st.rerun()
            else:
                st.error(f"❌ Error saving changes: {result.get('error')}")
    
    with col2:
        if st.button("📄 Save as New", use_container_width=True):
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
                st.success(f"✅ New version saved successfully! File: {Path(result.get('file_path', '')).name}")
            else:
                st.error(f"❌ Error saving new version: {result.get('error')}")
    
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
        and converts them into structured JSON format.
        
        **Supported Companies:**
        - Britannia
        - Colgate
        - Dabur
        - HUL
        - ITC
        - Nestlé
        - P&G
        """)
        
        st.divider()
        
        st.header("API Status")
        if api_status:
            st.success("✅ API is running")
        else:
            st.error("❌ API is not running")
            st.warning("Please start the Flask API server:\n```bash\npython app.py\n```")
    
    # Main content
    if not api_status:
        st.error("⚠️ Cannot connect to API server. Please ensure the Flask API is running.")
        st.code("python app.py", language="bash")
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Parse", "✏️ Review & Edit", "📊 View Results"])
    
    with tab1:
        st.header("Upload Financial Document")
        
        # Get supported companies
        companies = get_supported_companies()
        
        if not companies:
            st.error("Unable to fetch supported companies from API.")
            return
        
        # File upload
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose a PDF file",
                type=['pdf'],
                help="Upload a quarterly financial report in PDF format"
            )
        
        with col2:
            company_name = st.selectbox(
                "Select Company",
                options=companies,
                help="Select the company whose report you're uploading"
            )
        
        # Parse button
        if uploaded_file is not None:
            st.info(f"📄 **File:** {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("🚀 Parse Document", type="primary", use_container_width=True):
                    result = parse_document(uploaded_file, company_name)
                    
                    if result.get('success'):
                        st.session_state.parsed_data = result.get('data')
                        st.session_state.output_files = result.get('output_files', {})
                        st.session_state.processing_time = result.get('processing_time')
                        # Store document name (without extension)
                        st.session_state.document_name = Path(uploaded_file.name).stem
                        st.rerun()
                    else:
                        st.error(f"❌ {result.get('error', 'Unknown error')}")
            
            with col2:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.parsed_data = None
                    st.session_state.output_files = {}
                    st.rerun()
        
        # Display results if available
        if st.session_state.parsed_data:
            st.divider()
            st.success("✅ Document parsed successfully!")
            
            if st.session_state.get('processing_time'):
                processing_time = st.session_state.processing_time
                if isinstance(processing_time, (int, float)):
                    st.info(f"⏱️ Processing time: {processing_time:.2f} seconds")
                else:
                    st.info(f"⏱️ Processing time: {processing_time}")
            
            st.subheader("Extracted Financial Data (Preview)")
            display_financial_data(st.session_state.parsed_data)
            
            st.info("💡 Switch to the '✏️ Review & Edit' tab to review and modify the extracted data.")
            
            # Download options
            st.divider()
            st.subheader("📥 Download Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Download JSON
                json_str = json.dumps(st.session_state.parsed_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📄 Download JSON",
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
                            label="📊 Download CSV",
                            data=csv_data,
                            file_name=Path(csv_path).name,
                            mime="text/csv",
                            use_container_width=True
                        )
                    except:
                        st.button("📊 Download CSV", disabled=True, use_container_width=True)
            
            with col3:
                # Download Markdown (if available)
                if 'md_1' in st.session_state.output_files:
                    md_path = st.session_state.output_files['md_1']
                    try:
                        with open(md_path, 'r', encoding='utf-8') as f:
                            md_data = f.read()
                        st.download_button(
                            label="📝 Download Markdown",
                            data=md_data,
                            file_name=Path(md_path).name,
                            mime="text/markdown",
                            use_container_width=True
                        )
                    except:
                        st.button("📝 Download Markdown", disabled=True, use_container_width=True)
    
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


if __name__ == "__main__":
    main()
