"""
Test script for AI-powered Excel generation
Demonstrates the new AI extraction workflow
"""
import requests
import os
from pathlib import Path
import json

API_URL = "http://localhost:5000"

def test_api_health():
    """Test if API is running."""
    print("\n📡 Testing API Health...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"   Config loaded: {data['config_loaded']}")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {str(e)}")
        print("   Make sure to run: python app.py")
        return False


def test_ai_availability():
    """Test if AI extractor is initialized."""
    print("\n🤖 Testing AI Extractor Availability...")
    
    # Try a dummy request to see if AI is available
    response = requests.post(
        f"{API_URL}/api/generate-excel-ai",
        json={
            "company_name": "TEST",
            "document_name": "test"
        }
    )
    
    if response.status_code == 503:
        error = response.json()
        if 'OPENAI_API_KEY' in error.get('error', ''):
            print("❌ AI extractor not available - OPENAI_API_KEY not set")
            print("   Set environment variable: export OPENAI_API_KEY='sk-...'")
            return False
    
    print("✅ AI extractor is initialized")
    return True


def list_available_documents():
    """List all parsed documents available for AI extraction."""
    print("\n📁 Available Parsed Documents:")
    
    output_folder = Path("output")
    if not output_folder.exists():
        print("❌ No output folder found. Parse a document first.")
        return []
    
    documents = []
    for folder in output_folder.iterdir():
        if folder.is_dir():
            # Check if has table files
            table_files = list(folder.glob("*-table-*.html")) + list(folder.glob("*-table-*.md"))
            if table_files:
                # Extract company and document name
                folder_name = folder.name
                if '_' in folder_name:
                    parts = folder_name.split('_', 1)
                    company = parts[0]
                    doc_name = parts[1] if len(parts) > 1 else parts[0]
                    documents.append({
                        'company': company,
                        'document': doc_name,
                        'folder': folder_name,
                        'table_files': len(table_files)
                    })
                    print(f"   • {company}/{doc_name} ({len(table_files)} table files)")
    
    if not documents:
        print("❌ No parsed documents found. Run /api/parse first.")
    
    return documents


def test_ai_extraction(company, document):
    """Test AI extraction for a specific document."""
    print(f"\n🚀 Testing AI Extraction: {company}/{document}")
    
    payload = {
        "company_name": company,
        "document_name": document,
        "preferred_format": "html",
        "save": False
    }
    
    print("   Sending request to /api/generate-excel-ai...")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/generate-excel-ai",
            json=payload,
            timeout=120  # AI extraction can take time
        )
        
        if response.status_code == 200:
            # Check if it's JSON (save mode) or binary (download mode)
            content_type = response.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                data = response.json()
                print("✅ Excel generated and saved!")
                print(f"   File ID: {data.get('file_id')}")
                print(f"   Download URL: {data.get('download_url')}")
                
                if 'metadata' in data:
                    metadata = data['metadata']
                    print(f"   AI Model: {metadata.get('model', 'N/A')}")
                    print(f"   Tokens Used: {metadata.get('tokens_used', 'N/A')}")
                    print(f"   Source Format: {metadata.get('source_format', 'N/A')}")
            else:
                # Binary file response
                output_file = f"test_output_{company}_AI.xlsx"
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Excel file downloaded!")
                print(f"   Saved to: {output_file}")
                print(f"   Size: {len(response.content)} bytes")
            
            return True
        else:
            error = response.json()
            print(f"❌ Error: {error.get('error', 'Unknown error')}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - AI extraction took too long")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_with_save_mode(company, document):
    """Test AI extraction with save to storage."""
    print(f"\n💾 Testing Save Mode: {company}/{document}")
    
    payload = {
        "company_name": company,
        "document_name": document,
        "preferred_format": "html",
        "save": True  # Save to storage
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/generate-excel-ai",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Excel generated and saved!")
            print(f"   File ID: {data.get('file_id')}")
            
            # Test download
            file_id = data.get('file_id')
            print(f"\n📥 Testing download of saved file...")
            
            download_response = requests.get(
                f"{API_URL}/api/download-generated/{file_id}",
                timeout=30
            )
            
            if download_response.status_code == 200:
                output_file = f"test_saved_{company}_AI.xlsx"
                with open(output_file, 'wb') as f:
                    f.write(download_response.content)
                print(f"✅ Downloaded saved file!")
                print(f"   Saved to: {output_file}")
                return True
            else:
                print(f"❌ Failed to download: {download_response.status_code}")
                return False
        else:
            error = response.json()
            print(f"❌ Error: {error.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def run_comprehensive_test():
    """Run comprehensive test suite."""
    print("="*60)
    print("🧪 AI Excel Generator - Comprehensive Test Suite")
    print("="*60)
    
    # Test 1: API Health
    if not test_api_health():
        print("\n⚠️ Cannot proceed without API running")
        return
    
    # Test 2: AI Availability
    if not test_ai_availability():
        print("\n⚠️ Cannot proceed without OPENAI_API_KEY")
        return
    
    # Test 3: List available documents
    documents = list_available_documents()
    
    if not documents:
        print("\n⚠️ No documents to test. Please parse a document first:")
        print("   curl -X POST http://localhost:5000/api/parse \\")
        print("     -F 'file=@sample.pdf' \\")
        print("     -F 'company_name=BRITANNIA'")
        return
    
    # Test 4: AI Extraction (first document)
    if documents:
        doc = documents[0]
        success = test_ai_extraction(doc['company'], doc['document'])
        
        if success and len(documents) > 0:
            # Test 5: Save mode
            test_with_save_mode(doc['company'], doc['document'])
    
    print("\n" + "="*60)
    print("✅ Test suite completed!")
    print("="*60)


def interactive_test():
    """Interactive testing mode."""
    print("="*60)
    print("🎮 AI Excel Generator - Interactive Test")
    print("="*60)
    
    if not test_api_health():
        return
    
    if not test_ai_availability():
        return
    
    documents = list_available_documents()
    
    if not documents:
        print("\n⚠️ No documents available for testing")
        return
    
    print("\nSelect a document to test:")
    for i, doc in enumerate(documents):
        print(f"   {i+1}. {doc['company']} - {doc['document']}")
    
    try:
        choice = int(input("\nEnter number (or 0 to exit): "))
        
        if choice == 0:
            print("👋 Goodbye!")
            return
        
        if 1 <= choice <= len(documents):
            doc = documents[choice - 1]
            
            print("\nSelect test mode:")
            print("   1. Direct download")
            print("   2. Save to storage")
            
            mode = int(input("\nEnter mode: "))
            
            if mode == 1:
                test_ai_extraction(doc['company'], doc['document'])
            elif mode == 2:
                test_with_save_mode(doc['company'], doc['document'])
        else:
            print("❌ Invalid choice")
    
    except ValueError:
        print("❌ Invalid input")
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        run_comprehensive_test()
        
        print("\n💡 Tip: Run with --interactive flag for interactive mode:")
        print("   python test_ai_excel.py --interactive")
