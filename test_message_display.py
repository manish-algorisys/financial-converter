"""
Quick test to verify the update endpoint and message display
"""
import requests
import json

API_URL = "http://localhost:5000"

def test_health():
    """Test API health."""
    print("Testing API health...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running\n")
            return True
        else:
            print("❌ API returned non-200 status\n")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}\n")
        return False


def test_update_success():
    """Test successful update."""
    print("=" * 60)
    print("Test 1: Successful Update")
    print("=" * 60)
    
    data = {
        "company_name": "BRITANNIA",
        "document_name": "test_document",
        "financial_data": [
            {
                "particular": "Test Item",
                "key": "test_item",
                "values": {
                    "30.06.2025": "100.00",
                    "31.03.2025": "90.00"
                }
            }
        ],
        "create_new": False
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/update-financial-data",
            json=data,
            timeout=30
        )
        
        result = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("\n✅ SUCCESS case working correctly")
            print(f"Message: {result.get('message')}")
        else:
            print("\n❌ Expected success but got error")
            print(f"Error: {result.get('error')}")
        
    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")
    
    print("=" * 60 + "\n")


def test_update_error():
    """Test error handling."""
    print("=" * 60)
    print("Test 2: Error Handling (Missing company_name)")
    print("=" * 60)
    
    # Invalid data - missing company_name
    data = {
        "document_name": "test_document",
        "financial_data": [
            {
                "particular": "Test Item",
                "key": "test_item",
                "values": {"30.06.2025": "100.00"}
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/update-financial-data",
            json=data,
            timeout=30
        )
        
        result = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if not result.get('success'):
            print("\n✅ ERROR case working correctly")
            print(f"Error message: {result.get('error')}")
        else:
            print("\n❌ Expected error but got success")
        
    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")
    
    print("=" * 60 + "\n")


def test_invalid_company():
    """Test invalid company name."""
    print("=" * 60)
    print("Test 3: Invalid Company Name")
    print("=" * 60)
    
    data = {
        "company_name": "INVALID_COMPANY",
        "document_name": "test_document",
        "financial_data": [
            {
                "particular": "Test Item",
                "key": "test_item",
                "values": {"30.06.2025": "100.00"}
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/update-financial-data",
            json=data,
            timeout=30
        )
        
        result = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if not result.get('success'):
            print("\n✅ Validation working correctly")
            print(f"Error message: {result.get('error')}")
        else:
            print("\n❌ Expected validation error")
        
    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print("\n🧪 Testing Update Financial Data Endpoint\n")
    
    if test_health():
        print("Running tests...\n")
        test_update_success()
        test_update_error()
        test_invalid_company()
        
        print("\n" + "=" * 60)
        print("Testing Complete!")
        print("=" * 60)
        print("\n📝 Summary:")
        print("- Messages should appear in Streamlit UI after save")
        print("- Check that success messages show with ✅")
        print("- Check that error messages show with ❌")
        print("- Messages should persist after page rerun")
        print("\n💡 To test in UI:")
        print("1. Start: streamlit run streamlit_app.py")
        print("2. Parse a document")
        print("3. Go to 'Review & Edit' tab")
        print("4. Make an edit and click 'Save Changes'")
        print("5. Verify you see the success message!")
    else:
        print("⚠️  Please start the Flask API first:")
        print("   python app.py")
