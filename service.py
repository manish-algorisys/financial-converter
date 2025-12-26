
import logging
import time
from pathlib import Path
from pypdf import PdfReader
import re
import json
from bs4 import BeautifulSoup

import pandas as pd

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    EasyOcrOptions,
    TableFormerMode
)
from docling.datamodel.settings import settings


_log = logging.getLogger(__name__)

# -------------------------------------------------------------------
# 1. HEADING KEYWORDS FOR IDENTIFYING TARGET PAGE
# -------------------------------------------------------------------
# Primary patterns - with "standalone" explicitly mentioned
TARGET_HEADINGS_WITH_STANDALONE = [
    r"standalone.*financial.*result.*30.*june.*2025",
    r"statement of.*standalone.*30.*june.*2025",
]

# Secondary patterns - financial results without specifying standalone/consolidated
# These will be accepted only if "consolidated" is NOT found on the page
TARGET_HEADINGS_GENERIC = [
    r"statement of unaudited.*financial.*result.*30.*june.*2025",
    r"unaudited.*financial.*result.*30.*june.*2025",
    r"financial.*result.*quarter.*30.*june.*2025",
    r"sfatement of unaudiтed.*financial.*re5ulтs.*for тне quarter ended.*]une.*30,.*2025",
]

def find_target_page(pdf_path: Path) -> int | None:
    """Return page index containing the Standalone (not Consolidated) Unaudited Q1/Q2 June 2025 results."""
    reader = PdfReader(str(pdf_path))

    for page_index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text_lower = text.lower()

        # First, try patterns that explicitly mention "standalone"
        for pattern in TARGET_HEADINGS_WITH_STANDALONE:
            if re.search(pattern, text_lower):
                _log.info(f"Page {page_index + 1}: Found STANDALONE financial results (explicit)")
                return page_index

        # If no explicit standalone, check generic patterns
        # but ONLY if the page does NOT contain "consolidated"
        if "consolidated" not in text_lower:
            for pattern in TARGET_HEADINGS_GENERIC:
                if re.search(pattern, text_lower):
                    _log.info(f"Page {page_index + 1}: Found financial results (no consolidated keyword, assuming standalone)")
                    return page_index
        else:
            _log.info(f"Page {page_index + 1}: Skipping - contains 'consolidated' keyword")

    return None

# -------------------------------------------------------------------
# PARSE HTML TABLE AND CREATE JSON
# -------------------------------------------------------------------
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
            label_col_index = column_layout.get("label", 2) - 1  # Adjust for 0-indexing
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
                
                if col_index <= len(cells):
                    value = cells[col_index - 1].get_text(strip=True)
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

# -------------------------------------------------------------------
# MAIN EXTRACTOR
# -------------------------------------------------------------------
def main():
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path("sample-data/Britannia Unaudited Q2 June 2026.pdf")
    # input_doc_path = Path("sample-data/Colgate Unaudited Q2 June 2026.pdf")
    # input_doc_path = Path("sample-data/Dabur Unaudited Q2 June 2026.pdf")
    # input_doc_path = Path("sample-data/HUL Q2 June 2026.pdf")
    # input_doc_path = Path("sample-data/ITC Unaudited Q2 June 2026.pdf")
    # input_doc_path = Path("sample-data/Nestle Unaudited Q2 June 2026.pdf")
    # input_doc_path = Path("sample-data/P&G Unaudited Q2 June 2026.pdf")
    company_name = "BRITANNIA"
    # company_name = "COLGATE"
    # company_name = "DABUR"
    # company_name = "HUL"
    # company_name = "ITC"
    # company_name = "NESTLE"
    # company_name = "P&G"
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

     # STEP 1: Find the target page
    target_page = find_target_page(input_doc_path)

    if target_page is None:
        print("⚠️ Could not find Standalone Unaudited Financial Results page. Processing entire document...")
    else:
        print(f"✅ Target table found on page: {target_page + 1}")

    # Explicitly set the accelerator
    # accelerator_options = AcceleratorOptions(
    #     num_threads=8, device=AcceleratorDevice.AUTO
    # )
    accelerator_options = AcceleratorOptions(
        num_threads=8, device=AcceleratorDevice.CPU
    )
    # accelerator_options = AcceleratorOptions(
    #     num_threads=8, device=AcceleratorDevice.MPS
    # )
    # accelerator_options = AcceleratorOptions(
    #     num_threads=8, device=AcceleratorDevice.CUDA
    # )

    # easyocr doesnt support cuda:N allocation, defaults to cuda:0
    # accelerator_options = AcceleratorOptions(num_threads=8, device="cuda:1")

    pipeline_options = PdfPipelineOptions()
    pipeline_options.accelerator_options = accelerator_options
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
    pipeline_options.table_structure_options.do_cell_matching = True

    ocr_options = EasyOcrOptions(force_full_page_ocr=True)

    pipeline_options.ocr_options = ocr_options
    
    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                backend=PyPdfiumDocumentBackend
            ),
        }
    )

    # Enable the profiling to measure the time spent
    settings.debug.profile_pipeline_timings = True

    # STEP 2: Convert document (specific page if found, entire document otherwise)
    if target_page is not None:
        _log.info(f"Converting only page {target_page + 1}")
        conv_res = doc_converter.convert(input_doc_path, page_range=(target_page + 1, target_page + 1))
    else:
        _log.info("Converting entire document")
        conv_res = doc_converter.convert(input_doc_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    doc_filename = conv_res.input.file.stem

    # Export tables
    for table_ix, table in enumerate(conv_res.document.tables):
        table_df: pd.DataFrame = table.export_to_dataframe(doc=conv_res.document)

        _log.info(f"## Extracted Table {table_ix}")
        print(table_df.to_markdown())

        # Save the table as CSV
        element_csv_filename = output_dir / f"{doc_filename}-table-{table_ix + 1}.csv"
        _log.info(f"Saving CSV table to {element_csv_filename}")
        table_df.to_csv(element_csv_filename, encoding='utf-8')
        _log.info(f"Saved CSV table to {element_csv_filename}")

        # Save the table as HTML
        element_html_filename = output_dir / f"{doc_filename}-table-{table_ix + 1}.html"
        _log.info(f"Saving HTML table to {element_html_filename}")
        with element_html_filename.open("w", encoding='utf-8') as fp:
            fp.write(table.export_to_html(doc=conv_res.document))
        _log.info(f"Saved HTML table to {element_html_filename}")

        # Save the table as Markdown
        element_md_filename = output_dir / f"{doc_filename}-table-{table_ix + 1}.md"
        _log.info(f"Saving Markdown table to {element_md_filename}")
        with element_md_filename.open("w", encoding='utf-8') as fp:
            fp.write(table_df.to_markdown())
        _log.info(f"Saved Markdown table to {element_md_filename}")

    # List with total time per document
    doc_conversion_secs = conv_res.timings["pipeline_total"].times

    _log.info(f"\n🎉 Done — extracted only the Standalone Unaudited June 2025 financial results table in {doc_conversion_secs} seconds.")

    # Load config.json
    config_path = Path("config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Parse the first HTML table and create JSON output
    html_filename = output_dir / f"{doc_filename}-table-1.html"
    if html_filename.exists():
        _log.info(f"\n📊 Parsing HTML table and creating JSON output...")
        json_result = parse_html_table_to_json(html_filename, company_name, config)
        
        if json_result:
            # Print formatted JSON
            print("\n" + "="*80)
            print("FORMATTED JSON OUTPUT:")
            print("="*80)
            print(json.dumps(json_result, indent=2, ensure_ascii=False))
            print("="*80 + "\n")
            
            # Optionally save to file
            json_output_path = output_dir / f"{doc_filename}-financial-data.json"
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(json_result, f, indent=2, ensure_ascii=False)
            _log.info(f"💾 Saved JSON output to {json_output_path}")
    else:
        _log.warning(f"HTML file not found: {html_filename}")


if __name__ == "__main__":
    main()