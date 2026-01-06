"""
Test script for column mapping Excel template approach
"""
import json
import logging
from pathlib import Path
from excel_generator import FinancialExcelGenerator

# Enable DEBUG logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Create test data
test_data = {
    "company_name": "TEST COMPANY",
    "financial_data": [
        {
            "key": "sale_of_goods",
            "periods": {
                "30.06.2025": 15000.50,
                "31.03.2025": 14500.25,
                "30.06.2024": 13200.75,
                "31.03.2025_Y": 58000.00
            }
        },
        {
            "key": "export_sales",
            "periods": {
                "30.06.2025": 5000.00,
                "31.03.2025": 4800.00,
                "30.06.2024": 4500.00,
                "31.03.2025_Y": 19000.00
            }
        },
        {
            "key": "revenue_from_operations",
            "periods": {
                "30.06.2025": 25000.00,
                "31.03.2025": 24000.00,
                "30.06.2024": 22000.00,
                "31.03.2025_Y": 95000.00
            }
        },
        {
            "key": "net_profit",
            "periods": {
                "30.06.2025": 2500.00,
                "31.03.2025": 2300.00,
                "30.06.2024": 2100.00,
                "31.03.2025_Y": 9500.00
            }
        },
        {
            "key": "eps_basic",
            "periods": {
                "30.06.2025": 12.50,
                "31.03.2025": 11.80,
                "30.06.2024": 10.90,
                "31.03.2025_Y": 48.20
            }
        }
    ]
}

def test_column_mapping():
    """Test column mapping template approach"""
    print("Testing Column Mapping Template Approach")
    print("=" * 60)
    
    # Setup paths
    template_path = Path("templates/financial_summary_template_column_mapping.xlsx")
    output_path = Path("test_column_mapping_output.xlsx")
    
    # Check template exists
    if not template_path.exists():
        print(f"[ERROR] Template not found: {template_path}")
        return False
    
    print(f"[OK] Using template: {template_path}")
    
    # Generate Excel
    generator = FinancialExcelGenerator()
    
    try:
        success = generator.generate_excel(
            json_data=test_data,
            output_path=output_path,
            template_excel_path=template_path
        )
        
        if success:
            print(f"[OK] Excel generated successfully: {output_path}")
            print("\nTest completed successfully!")
            print(f"\nOpen the file to verify: {output_path.absolute()}")
            return True
        else:
            print("[ERROR] Excel generation failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error during generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_column_mapping()
