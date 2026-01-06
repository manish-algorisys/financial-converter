"""
Test multi-company consolidation feature
"""
import requests
import json
from pathlib import Path

API_URL = "http://localhost:5000"

def test_multi_company_consolidation():
    """Test generating consolidated Excel from multiple companies."""
    
    # Check available parsed documents
    output_folder = Path("output")
    available_docs = []
    
    for folder in output_folder.glob("*_*"):
        parts = folder.name.split('_', 1)
        if len(parts) == 2:
            company_name = parts[0]
            doc_name = parts[1]
            available_docs.append({
                'company': company_name,
                'document': doc_name,
                'folder': folder.name
            })
    
    print(f"Found {len(available_docs)} parsed documents:")
    for doc in available_docs:
        print(f"  - {doc['company']}: {doc['document']}")
    
    if len(available_docs) < 2:
        print("\n⚠️ Need at least 2 parsed documents to test consolidation")
        print("Please parse at least 2 different company documents first")
        return
    
    # Select first 2 documents for testing
    selected_docs = available_docs[:2]
    
    print(f"\n📊 Testing consolidation with:")
    for doc in selected_docs:
        print(f"  - {doc['company']}: {doc['document']}")
    
    # Prepare API request
    documents_array = [
        {'company': doc['company'], 'document': doc['document']}
        for doc in selected_docs
    ]
    
    # Call consolidated API endpoint
    print("\n🔄 Calling /api/generate-excel-ai-consolidated...")
    
    response = requests.post(
        f"{API_URL}/api/generate-excel-ai-consolidated",
        data={
            'documents': json.dumps(documents_array),
            'preferred_format': 'html',
            'save': 'false'
        },
        timeout=300
    )
    
    if response.status_code == 200:
        # Save the returned Excel file
        output_file = Path("test_consolidated.xlsx")
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        print(f"\n✅ Success! Consolidated Excel saved to: {output_file}")
        print(f"   File size: {output_file.stat().st_size / 1024:.2f} KB")
        
        # Try to open with Excel (Windows)
        try:
            import os
            os.startfile(str(output_file.absolute()))
            print("   Opened in Excel")
        except:
            print("   Please open manually to review")
    else:
        print(f"\n❌ Error: {response.status_code}")
        try:
            error_data = response.json()
            print(f"   {error_data.get('error', 'Unknown error')}")
        except:
            print(f"   {response.text}")

if __name__ == "__main__":
    print("=" * 60)
    print("Multi-Company Consolidation Test")
    print("=" * 60)
    
    try:
        test_multi_company_consolidation()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to Flask API")
        print("   Please start the Flask server first:")
        print("   python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
