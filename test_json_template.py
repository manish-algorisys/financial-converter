"""
Test script for JSON Template Feature
Tests the template-based Excel generation without running the full app.
"""
import json
from pathlib import Path
from excel_generator import FinancialExcelGenerator

def test_json_template():
    """Test generating Excel from JSON template"""
    
    # Load default template
    template_path = Path('excel_template_default.json')
    
    if not template_path.exists():
        print("❌ Template file not found: excel_template_default.json")
        return False
    
    # Load and validate template
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    print("✅ Template loaded successfully")
    print(f"   - Title: {template.get('title', 'N/A')}")
    print(f"   - Template Name: {template.get('template_name', 'N/A')}")
    print(f"   - Columns: {len(template.get('columns', []))}")
    print(f"   - Rows: {len(template.get('rows', []))}")
    
    # Create sample extracted data
    sample_data = {
        "company_name": "TEST COMPANY LIMITED",
        "periods": {
            "30.06.2025": {"label": "Q1 FY2026", "description": "3M-30th Jun 2025"},
            "30.06.2024": {"label": "Q1 FY2025", "description": "3M-30th Jun 2024"},
            "31.03.2025_Y": {"label": "FY 2025", "description": "12M-31st Mar 2025"}
        },
        "financial_data": {
            "sale_of_goods": {
                "30.06.2025": 123456789.50,
                "30.06.2024": 115234567.25,
                "31.03.2025_Y": 478901234.75
            },
            "export_sales": {
                "30.06.2025": 45678912.30,
                "30.06.2024": 42345678.90,
                "31.03.2025_Y": 178901234.50
            },
            "revenue_from_operations": {
                "30.06.2025": 169135701.80,
                "30.06.2024": 157580246.15,
                "31.03.2025_Y": 657802469.25
            },
            "cost_of_materials": {
                "30.06.2025": -67654321.20,
                "30.06.2024": -63012345.60,
                "31.03.2025_Y": -263120987.30
            },
            "profit_for_the_period": {
                "30.06.2025": 25678901.40,
                "30.06.2024": 23456789.50,
                "31.03.2025_Y": 98765432.10
            }
        }
    }
    
    # Generate Excel using template
    generator = FinancialExcelGenerator()
    output_path = Path('test_output_template.xlsx')
    
    print("\n🔄 Generating Excel with template...")
    success = generator.generate_excel(
        sample_data,
        output_path,
        template_json_path=template_path
    )
    
    if success and output_path.exists():
        print(f"✅ Excel generated successfully: {output_path}")
        print(f"   - File size: {output_path.stat().st_size / 1024:.2f} KB")
        return True
    else:
        print("❌ Failed to generate Excel")
        return False

def test_without_template():
    """Test generating Excel without template (fixed format)"""
    
    # Create sample extracted data
    sample_data = {
        "company_name": "TEST COMPANY LIMITED (Fixed Format)",
        "periods": {
            "30.06.2025": {"label": "Q1 FY2026", "description": "3M-30th Jun 2025"},
            "30.06.2024": {"label": "Q1 FY2025", "description": "3M-30th Jun 2024"}
        },
        "financial_data": {
            "sale_of_goods": {
                "30.06.2025": 123456789.50,
                "30.06.2024": 115234567.25
            },
            "revenue_from_operations": {
                "30.06.2025": 169135701.80,
                "30.06.2024": 157580246.15
            }
        }
    }
    
    # Generate Excel without template
    generator = FinancialExcelGenerator()
    output_path = Path('test_output_fixed.xlsx')
    
    print("\n🔄 Generating Excel without template (fixed format)...")
    success = generator.generate_excel(sample_data, output_path)
    
    if success and output_path.exists():
        print(f"✅ Excel generated successfully: {output_path}")
        print(f"   - File size: {output_path.stat().st_size / 1024:.2f} KB")
        return True
    else:
        print("❌ Failed to generate Excel")
        return False

def validate_template_structure():
    """Validate template JSON structure"""
    
    template_path = Path('excel_template_default.json')
    
    if not template_path.exists():
        print("❌ Template not found")
        return False
    
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    print("\n🔍 Validating template structure...")
    
    # Check required fields
    required_fields = ['columns', 'rows', 'formatting', 'layout']
    missing = [f for f in required_fields if f not in template]
    
    if missing:
        print(f"❌ Missing required fields: {missing}")
        return False
    
    print("✅ All required fields present")
    
    # Validate columns
    columns = template.get('columns', [])
    if not columns:
        print("❌ No columns defined")
        return False
    
    for i, col in enumerate(columns):
        if 'period' not in col or 'label' not in col:
            print(f"❌ Column {i} missing period or label")
            return False
    
    print(f"✅ {len(columns)} columns validated")
    
    # Validate rows
    rows = template.get('rows', [])
    if not rows:
        print("❌ No rows defined")
        return False
    
    valid_types = ['section_header', 'data', 'total', 'metric', 'blank']
    for i, row in enumerate(rows):
        if 'type' not in row or 'label' not in row:
            print(f"❌ Row {i} missing type or label")
            return False
        
        if row['type'] not in valid_types:
            print(f"❌ Row {i} has invalid type: {row['type']}")
            return False
        
        if row['type'] == 'data' and 'key' not in row:
            print(f"⚠️  Row {i} is data type but missing key")
    
    print(f"✅ {len(rows)} rows validated")
    
    # Validate formatting
    formatting = template.get('formatting', {})
    print(f"✅ {len(formatting)} formatting rules defined")
    
    # Validate layout
    layout = template.get('layout', {})
    required_layout_fields = ['title_row', 'period_header_row', 'data_start_row']
    missing_layout = [f for f in required_layout_fields if f not in layout]
    
    if missing_layout:
        print(f"⚠️  Missing layout fields: {missing_layout}")
    else:
        print("✅ Layout configuration complete")
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("JSON TEMPLATE FEATURE - TEST SUITE")
    print("=" * 60)
    
    # Test 1: Validate template structure
    print("\nTest 1: Template Structure Validation")
    print("-" * 60)
    result1 = validate_template_structure()
    
    # Test 2: Generate with template
    print("\nTest 2: Excel Generation with Template")
    print("-" * 60)
    result2 = test_json_template()
    
    # Test 3: Generate without template (backward compatibility)
    print("\nTest 3: Excel Generation without Template (Fixed Format)")
    print("-" * 60)
    result3 = test_without_template()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Template Validation: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Template Generation: {'✅ PASS' if result2 else '❌ FAIL'}")
    print(f"Fixed Format (Backward Compatibility): {'✅ PASS' if result3 else '❌ FAIL'}")
    
    all_passed = result1 and result2 and result3
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    print("=" * 60)
    
    if all_passed:
        print("\n✨ JSON Template feature is working correctly!")
        print("\nGenerated files:")
        print("  - test_output_template.xlsx (with template)")
        print("  - test_output_fixed.xlsx (fixed format)")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
