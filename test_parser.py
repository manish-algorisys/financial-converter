import json
from pathlib import Path
from bs4 import BeautifulSoup
import logging

_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def parse_html_table_to_json(html_file_path: Path, company_name: str, config: dict) -> dict:
    """Parse HTML table and create JSON output based on config."""
    
    # Map company name to config key
    company_mapping = {
        "BRITANNIA": "britannia",
        "COLGATE": "colgate",
        "DABUR": "dabur",
        "HUL": "hul",
        "ITC": "itc",
        "NESTLE": "nestle",
        "P&G": "pg"
    }
    
    config_key = company_mapping.get(company_name)
    if not config_key:
        _log.error(f"Unknown company name: {company_name}")
        return None
    
    company_config = config.get(config_key)
    if not company_config:
        _log.error(f"No configuration found for {config_key}")
        return None
    
    # Get column layout
    column_layout_name = company_config.get("column_layout", "standard")
    column_layout = config["column_layouts"][column_layout_name]
    
    # Read HTML file
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    
    if not table:
        _log.error("No table found in HTML file")
        return None
    
    # Extract all rows
    rows = table.find_all('tr')
    
    # Create result structure
    result = {
        "company_name": company_name,
        "financial_data": []
    }
    
    # Process each financial data item from config
    for item_config in company_config["financial_data"]:
        key = item_config["key"]
        labels = item_config["labels"]
        tr_number = item_config.get("tr_number", 0)
        
        # Use tr_number to directly access the row
        if tr_number > 0 and tr_number <= len(rows):
            matched_row = rows[tr_number - 1]  # tr_number is 1-indexed
            
            # Extract values from the row based on column layout
            cells = matched_row.find_all(['td', 'th'])
            
            # Get the label from the label column
            label_col_index = column_layout.get("label", 2)
            particular = ""
            if label_col_index < len(cells):
                particular = cells[label_col_index].get_text(strip=True)
            
            # If particular is empty, try to find it from the labels list
            if not particular:
                particular = labels[0] if labels else key
            
            values = {}
            for date_key, col_index in column_layout.items():
                if date_key == "label":
                    continue
                
                if col_index < len(cells):
                    value = cells[col_index].get_text(strip=True)
                    values[date_key] = value
                else:
                    values[date_key] = ""
            
            # Add to result
            result["financial_data"].append({
                "particular": particular,
                "key": key,
                "values": values
            })
        else:
            _log.warning(f"Invalid tr_number {tr_number} for key: {key} (total rows: {len(rows)})")
    
    return result


def main():
    # Load config.json
    config_path = Path("config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Parse the Britannia HTML table
    html_file = Path("output/Britannia Unaudited Q2 June 2026-table-1.html")
    company_name = "BRITANNIA"
    
    if html_file.exists():
        _log.info(f"📊 Parsing HTML table for {company_name}...")
        json_result = parse_html_table_to_json(html_file, company_name, config)
        
        if json_result:
            # Print formatted JSON
            print("\n" + "="*80)
            print("FORMATTED JSON OUTPUT:")
            print("="*80)
            print(json.dumps(json_result, indent=2, ensure_ascii=False))
            print("="*80 + "\n")
            
            # Save to file
            output_dir = Path("output")
            json_output_path = output_dir / f"{company_name}-financial-data.json"
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(json_result, f, indent=2, ensure_ascii=False)
            _log.info(f"💾 Saved JSON output to {json_output_path}")
        else:
            _log.error("Failed to parse HTML table")
    else:
        _log.error(f"HTML file not found: {html_file}")


if __name__ == "__main__":
    main()
