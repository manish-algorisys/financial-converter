"""
Test script to verify the installation and basic functionality
"""
import sys
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing imports...")
    
    packages = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('streamlit', 'Streamlit'),
        ('docling', 'Docling'),
        ('pandas', 'Pandas'),
        ('pypdf', 'PyPDF'),
        ('bs4', 'BeautifulSoup4'),
        ('easyocr', 'EasyOCR'),
    ]
    
    failed = []
    for package, name in packages:
        try:
            __import__(package)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name}: {str(e)}")
            failed.append(name)
    
    return len(failed) == 0


def test_config():
    """Test if config.json is valid."""
    print("\nTesting configuration...")
    
    try:
        from parser_core import load_config
        config = load_config()
        
        if config:
            print(f"✓ Configuration loaded")
            print(f"  - Column layouts: {len(config.get('column_layouts', {}))}")
            
            companies = ['britannia', 'colgate', 'dabur', 'hul', 'itc', 'nestle', 'pg']
            for company in companies:
                if company in config:
                    print(f"  - {company.upper()}: {len(config[company].get('financial_data', []))} metrics")
                else:
                    print(f"  ✗ {company.upper()}: Not found")
            
            return True
        else:
            print("✗ Configuration is empty")
            return False
            
    except Exception as e:
        print(f"✗ Configuration error: {str(e)}")
        return False


def test_directories():
    """Test if required directories exist."""
    print("\nTesting directories...")
    
    dirs = [
        'sample-data',
        'output',
        'uploads'
    ]
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✓ {dir_name}/ exists")
        else:
            print(f"✗ {dir_name}/ missing (will be created automatically)")
    
    return True


def test_sample_files():
    """Test if sample files exist."""
    print("\nTesting sample files...")
    
    sample_dir = Path('sample-data')
    if not sample_dir.exists():
        print("✗ sample-data directory not found")
        return False
    
    pdf_files = list(sample_dir.glob('*.pdf'))
    if pdf_files:
        print(f"✓ Found {len(pdf_files)} sample PDF file(s)")
        for pdf in pdf_files[:3]:  # Show first 3
            print(f"  - {pdf.name}")
        if len(pdf_files) > 3:
            print(f"  ... and {len(pdf_files) - 3} more")
    else:
        print("⚠ No sample PDF files found in sample-data/")
    
    return True


def test_core_functions():
    """Test core parsing functions."""
    print("\nTesting core functions...")
    
    try:
        from parser_core import get_supported_companies
        companies = get_supported_companies()
        print(f"✓ get_supported_companies(): {len(companies)} companies")
        print(f"  {', '.join(companies)}")
        return True
    except Exception as e:
        print(f"✗ Error testing core functions: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Financial Document Parser - Installation Test")
    print("=" * 60)
    print()
    
    results = {
        'Imports': test_imports(),
        'Configuration': test_config(),
        'Directories': test_directories(),
        'Sample Files': test_sample_files(),
        'Core Functions': test_core_functions(),
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20s}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! You're ready to go.")
        print("\nNext steps:")
        print("1. Run Flask API: python app.py")
        print("2. Run Streamlit UI: streamlit run streamlit_app.py")
        print("3. Or use the launcher: start.bat (Windows) or ./start.sh (Linux/Mac)")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("1. Activate virtual environment: venv\\Scripts\\activate (Windows)")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check config.json exists and is valid")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
