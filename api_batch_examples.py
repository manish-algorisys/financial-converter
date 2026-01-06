"""
API Examples for Batch Processing with Auto-Detection
Demonstrates usage of new batch endpoints
"""
import requests
from pathlib import Path

API_URL = "http://localhost:5000"

def test_single_file_auto_detection():
    """Test single file parsing with auto-detection (no company_name provided)"""
    print("\n" + "="*60)
    print("TEST 1: Single File with Auto-Detection")
    print("="*60)
    
    pdf_path = "sample-data/Britannia Unaudited Q2 June 2026.pdf"
    
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        data = {
            'prefer_standalone': 'true',
            'use_fuzzy_matching': 'true'
            # Note: NO company_name - will auto-detect
        }
        
        response = requests.post(f"{API_URL}/api/parse", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"   Detected Company: {result.get('detected_company', 'N/A')}")
        print(f"   Items Extracted: {len(result['data']['financial_data'])}")
        print(f"   Processing Time: {result['processing_time']:.2f}s")
        print(f"   Message: {result['message']}")
    else:
        print(f"❌ Failed: {response.json()}")


def test_batch_upload():
    """Test batch processing with multiple files"""
    print("\n" + "="*60)
    print("TEST 2: Batch Upload (Multiple Files)")
    print("="*60)
    
    pdf_files = [
        "sample-data/Britannia Unaudited Q2 June 2026.pdf",
        "sample-data/ITC Unaudited Q2 June 2026.pdf",
        "sample-data/P&G Unaudited Q2 June 2026.pdf"
    ]
    
    files = []
    for pdf_path in pdf_files:
        if Path(pdf_path).exists():
            files.append(('files[]', (Path(pdf_path).name, open(pdf_path, 'rb'), 'application/pdf')))
    
    data = {
        'prefer_standalone': 'true',
        'use_fuzzy_matching': 'true'
    }
    
    response = requests.post(f"{API_URL}/api/parse-batch", files=files, data=data)
    
    # Close file handles
    for _, (_, f, _) in files:
        f.close()
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Batch processing completed!")
        print(f"\nSummary:")
        print(f"   Total Files: {result['summary']['total']}")
        print(f"   Successful: {result['summary']['successful']}")
        print(f"   Failed: {result['summary']['failed']}")
        
        print(f"\nResults:")
        for idx, file_result in enumerate(result['results'], 1):
            status = "✅" if file_result['success'] else "❌"
            company = file_result.get('detected_company', 'N/A')
            filename = file_result['filename']
            print(f"   {status} {filename} - {company}")
            if not file_result['success']:
                print(f"      Error: {file_result.get('error', 'Unknown')}")
    else:
        print(f"❌ Failed: {response.json()}")


def test_folder_parsing():
    """Test folder-based parsing"""
    print("\n" + "="*60)
    print("TEST 3: Folder Parsing")
    print("="*60)
    
    payload = {
        "folder_path": "sample-data",
        "prefer_standalone": True,
        "use_fuzzy_matching": True
    }
    
    response = requests.post(
        f"{API_URL}/api/parse-folder",
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Folder processing completed!")
        print(f"\nSummary:")
        print(f"   Total Files: {result['summary']['total']}")
        print(f"   Successful: {result['summary']['successful']}")
        print(f"   Failed: {result['summary']['failed']}")
        
        print(f"\nResults:")
        for idx, file_result in enumerate(result['results'], 1):
            status = "✅" if file_result['success'] else "❌"
            company = file_result.get('detected_company', 'N/A')
            filename = file_result['filename']
            print(f"   {status} {filename} - {company}")
            if file_result['success']:
                print(f"      Items: {len(file_result['data']['financial_data'])}, Time: {file_result['processing_time']:.2f}s")
            else:
                print(f"      Error: {file_result.get('error', 'Unknown')}")
    else:
        print(f"❌ Failed: {response.json()}")


def test_manual_company_override():
    """Test providing company_name manually (override auto-detection)"""
    print("\n" + "="*60)
    print("TEST 4: Manual Company Override")
    print("="*60)
    
    pdf_path = "sample-data/Britannia Unaudited Q2 June 2026.pdf"
    
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        data = {
            'company_name': 'BRITANNIA',  # Manually specified
            'prefer_standalone': 'true',
            'use_fuzzy_matching': 'true'
        }
        
        response = requests.post(f"{API_URL}/api/parse", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"   Company (Manual): BRITANNIA")
        print(f"   Auto-detection used: {'detected_company' in result}")
        print(f"   Items Extracted: {len(result['data']['financial_data'])}")
        print(f"   Processing Time: {result['processing_time']:.2f}s")
    else:
        print(f"❌ Failed: {response.json()}")


if __name__ == "__main__":
    print("\n🚀 Testing Financial Parser API - Batch Processing with Auto-Detection")
    print("Make sure Flask API is running on http://localhost:5000")
    
    try:
        # Check API health
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not responding. Please start the Flask server.")
            exit(1)
        
        print("✅ API is running\n")
        
        # Run tests
        test_single_file_auto_detection()
        test_manual_company_override()
        test_batch_upload()
        test_folder_parsing()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Please ensure Flask server is running:")
        print("   python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
