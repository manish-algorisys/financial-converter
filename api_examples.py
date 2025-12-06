"""
Example scripts for using the Financial Document Parser API
"""
import requests
import json
from pathlib import Path

# API Configuration
API_BASE_URL = "http://localhost:5000"


def example_1_health_check():
    """Example 1: Check if API is running."""
    print("=" * 60)
    print("Example 1: Health Check")
    print("=" * 60)
    
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def example_2_get_companies():
    """Example 2: Get list of supported companies."""
    print("=" * 60)
    print("Example 2: Get Supported Companies")
    print("=" * 60)
    
    response = requests.get(f"{API_BASE_URL}/api/companies")
    data = response.json()
    
    if data.get('success'):
        print("Supported Companies:")
        for company in data['companies']:
            print(f"  - {company}")
    else:
        print(f"Error: {data.get('error')}")
    print()


def example_3_parse_document(pdf_path, company_name):
    """Example 3: Parse a financial document."""
    print("=" * 60)
    print("Example 3: Parse Document")
    print("=" * 60)
    
    # Check if file exists
    if not Path(pdf_path).exists():
        print(f"Error: File not found: {pdf_path}")
        return
    
    print(f"Uploading: {pdf_path}")
    print(f"Company: {company_name}")
    print("Processing... (this may take 30-60 seconds)")
    
    # Prepare the request
    with open(pdf_path, 'rb') as f:
        files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
        data = {'company_name': company_name}
        
        # Send request
        response = requests.post(
            f"{API_BASE_URL}/api/parse",
            files=files,
            data=data,
            timeout=300  # 5 minutes
        )
    
    # Process response
    result = response.json()
    
    if result.get('success'):
        print("\n✓ Success!")
        print(f"Message: {result['message']}")
        
        if result.get('processing_time'):
            print(f"Processing Time: {result['processing_time']:.2f} seconds")
        
        # Display financial data
        if result.get('data'):
            print("\nExtracted Financial Data:")
            print(f"Company: {result['data']['company_name']}")
            print(f"Number of metrics: {len(result['data'].get('financial_data', []))}")
            
            # Show first few items
            print("\nSample metrics:")
            for item in result['data']['financial_data'][:5]:
                print(f"  - {item['key']}: {item['particular']}")
        
        # Display output files
        if result.get('output_files'):
            print("\nGenerated Files:")
            for file_type, file_path in result['output_files'].items():
                print(f"  - {file_type}: {Path(file_path).name}")
        
        # Save full response to file
        output_file = f"api_response_{company_name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nFull response saved to: {output_file}")
        
    else:
        print(f"\n✗ Error: {result.get('error')}")
    
    print()


def example_4_parse_multiple_documents():
    """Example 4: Parse multiple documents."""
    print("=" * 60)
    print("Example 4: Parse Multiple Documents")
    print("=" * 60)
    
    # List of documents to process
    documents = [
        ("sample-data/Britannia Unaudited Q2 June 2026.pdf", "BRITANNIA"),
        ("sample-data/Colgate Unaudited Q2 June 2026.pdf", "COLGATE"),
        # Add more as needed
    ]
    
    results = []
    
    for pdf_path, company_name in documents:
        if not Path(pdf_path).exists():
            print(f"Skipping {pdf_path} (file not found)")
            continue
        
        print(f"\nProcessing: {Path(pdf_path).name}")
        
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
            data = {'company_name': company_name}
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/parse",
                    files=files,
                    data=data,
                    timeout=300
                )
                
                result = response.json()
                results.append({
                    'file': Path(pdf_path).name,
                    'company': company_name,
                    'success': result.get('success'),
                    'message': result.get('message') or result.get('error')
                })
                
                status = "✓" if result.get('success') else "✗"
                print(f"{status} {company_name}: {result.get('message') or result.get('error')}")
                
            except Exception as e:
                print(f"✗ {company_name}: Error - {str(e)}")
                results.append({
                    'file': Path(pdf_path).name,
                    'company': company_name,
                    'success': False,
                    'message': str(e)
                })
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    successful = sum(1 for r in results if r['success'])
    print(f"Total: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    print()


def example_5_export_to_excel():
    """Example 5: Parse document and convert to Excel."""
    print("=" * 60)
    print("Example 5: Export to Excel (requires openpyxl)")
    print("=" * 60)
    
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas is required. Install with: pip install pandas openpyxl")
        return
    
    # Parse document first
    pdf_path = "sample-data/Britannia Unaudited Q2 June 2026.pdf"
    company_name = "BRITANNIA"
    
    if not Path(pdf_path).exists():
        print(f"Error: File not found: {pdf_path}")
        return
    
    print(f"Processing: {pdf_path}")
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
        data = {'company_name': company_name}
        
        response = requests.post(
            f"{API_BASE_URL}/api/parse",
            files=files,
            data=data,
            timeout=300
        )
    
    result = response.json()
    
    if result.get('success') and result.get('data'):
        # Convert to DataFrame
        rows = []
        for item in result['data']['financial_data']:
            row = {'Particular': item['particular'], 'Key': item['key']}
            row.update(item['values'])
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Save to Excel
        excel_file = f"{company_name}_financial_data.xlsx"
        df.to_excel(excel_file, index=False, sheet_name='Financial Data')
        
        print(f"✓ Data exported to: {excel_file}")
    else:
        print(f"✗ Error: {result.get('error')}")
    
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Financial Document Parser - API Usage Examples")
    print("=" * 60)
    print()
    print("Make sure the Flask API is running: python app.py")
    print()
    input("Press Enter to continue...")
    print()
    
    # Run examples
    example_1_health_check()
    example_2_get_companies()
    
    # Example 3: Parse a single document
    # Uncomment and modify path as needed
    # example_3_parse_document(
    #     "sample-data/Britannia Unaudited Q2 June 2026.pdf",
    #     "BRITANNIA"
    # )
    
    # Example 4: Parse multiple documents
    # example_4_parse_multiple_documents()
    
    # Example 5: Export to Excel
    # example_5_export_to_excel()
    
    print("=" * 60)
    print("Examples completed!")
    print("\nTo run specific examples, uncomment them in the main() function.")
    print("=" * 60)


if __name__ == "__main__":
    main()
