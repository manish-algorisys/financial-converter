"""
Test script for the edit/update financial data endpoint
"""
import requests
import json

API_URL = "http://localhost:5000"

def test_update_endpoint():
    """Test the update financial data endpoint."""
    
    # Sample updated financial data
    sample_data = {
        "company_name": "BRITANNIA",
        "document_name": "Britannia Unaudited Q2 June 2026",
        "financial_data": [
            {
                "particular": "Sale of goods",
                "key": "sale_of_goods",
                "values": {
                    "30.06.2025": "1000.00",
                    "31.03.2025": "950.00",
                    "30.06.2024": "900.00",
                    "31.03.2025_Y": "3800.00"
                }
            },
            {
                "particular": "Other operating revenues",
                "key": "other_operating_revenues",
                "values": {
                    "30.06.2025": "50.00",
                    "31.03.2025": "45.00",
                    "30.06.2024": "40.00",
                    "31.03.2025_Y": "180.00"
                }
            }
        ],
        "create_new": False  # Set to True to create a new edited version
    }
    
    print("=" * 60)
    print("Testing Update Financial Data Endpoint")
    print("=" * 60)
    print(f"\nUpdating data for: {sample_data['company_name']}")
    print(f"Document: {sample_data['document_name']}")
    print(f"Number of metrics: {len(sample_data['financial_data'])}")
    print(f"Create new version: {sample_data['create_new']}")
    
    # Send request
    response = requests.post(
        f"{API_URL}/api/update-financial-data",
        json=sample_data,
        timeout=30
    )
    
    # Process response
    result = response.json()
    
    print("\n" + "-" * 60)
    print("Response:")
    print("-" * 60)
    print(json.dumps(result, indent=2))
    
    if result.get('success'):
        print("\n✅ Success!")
        print(f"File saved to: {result.get('file_path')}")
    else:
        print("\n❌ Error!")
        print(f"Error message: {result.get('error')}")
    
    print("=" * 60)


def test_create_new_version():
    """Test creating a new edited version."""
    
    sample_data = {
        "company_name": "BRITANNIA",
        "document_name": "Britannia Unaudited Q2 June 2026",
        "financial_data": [
            {
                "particular": "Sale of goods (EDITED)",
                "key": "sale_of_goods",
                "values": {
                    "30.06.2025": "1100.00",
                    "31.03.2025": "1050.00",
                    "30.06.2024": "1000.00",
                    "31.03.2025_Y": "4200.00"
                }
            }
        ],
        "create_new": True  # Create a new file
    }
    
    print("\n" + "=" * 60)
    print("Testing Create New Edited Version")
    print("=" * 60)
    
    response = requests.post(
        f"{API_URL}/api/update-financial-data",
        json=sample_data,
        timeout=30
    )
    
    result = response.json()
    
    print("Response:")
    print(json.dumps(result, indent=2))
    
    if result.get('success'):
        print("\n✅ New version created!")
        print(f"File: {result.get('file_path')}")
    else:
        print("\n❌ Error!")
        print(f"Error: {result.get('error')}")
    
    print("=" * 60)


if __name__ == "__main__":
    print("\n🧪 Financial Data Update Endpoint Tests\n")
    print("Make sure the Flask API is running: python app.py\n")
    
    try:
        # Check API health
        health = requests.get(f"{API_URL}/health", timeout=5)
        if health.status_code == 200:
            print("✅ API is running\n")
            
            # Run tests
            test_update_endpoint()
            input("\nPress Enter to test creating a new version...")
            test_create_new_version()
            
        else:
            print("❌ API is not responding correctly")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Please start the Flask server:")
        print("   python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
