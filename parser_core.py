"""
Core parsing functions extracted from service.py for reusability.
"""
import logging
import json
from pathlib import Path
from pypdf import PdfReader
import re
import pandas as pd
from bs4 import BeautifulSoup

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
# HEADING KEYWORDS FOR IDENTIFYING TARGET PAGE
# -------------------------------------------------------------------
TARGET_HEADINGS_WITH_STANDALONE = [
    r"standalone.*financial.*result.*30.*june.*2025",
    r"statement of.*standalone.*30.*june.*2025",
]

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
        override_column_layout = item_config.get("column_layout", None)

        if override_column_layout:
            column_layout = config["column_layouts"][override_column_layout]
        else:
            column_layout_name = company_config.get("column_layout", "standard")
            column_layout = config["column_layouts"][column_layout_name]
        
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


def process_pdf_document(pdf_path: Path, company_name: str, output_dir: Path, config: dict) -> dict:
    """
    Main function to process a PDF document and extract financial data.
    
    Args:
        pdf_path: Path to the PDF file
        company_name: Name of the company (must match config keys)
        output_dir: Directory to save output files
        config: Configuration dictionary with parsing rules
    
    Returns:
        Dictionary with:
        - success: bool
        - message: str
        - json_result: dict (if successful)
        - output_files: dict of generated file paths
    """
    try:
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find target page
        target_page = find_target_page(pdf_path)
        
        if target_page is None:
            _log.warning("Could not find Standalone Unaudited Financial Results page. Processing entire document...")
        else:
            _log.info(f"Target table found on page: {target_page + 1}")
        
        # Configure accelerator
        accelerator_options = AcceleratorOptions(
            num_threads=8, device=AcceleratorDevice.CPU
        )
        
        # Configure pipeline
        pipeline_options = PdfPipelineOptions()
        pipeline_options.accelerator_options = accelerator_options
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        pipeline_options.table_structure_options.do_cell_matching = True
        
        ocr_options = EasyOcrOptions(force_full_page_ocr=True)
        pipeline_options.ocr_options = ocr_options
        
        # Create document converter
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
        
        # Convert document
        if target_page is not None:
            _log.info(f"Converting only page {target_page + 1}")
            conv_res = doc_converter.convert(pdf_path, page_range=(target_page + 1, target_page + 1))
        else:
            _log.info("Converting entire document")
            conv_res = doc_converter.convert(pdf_path)
        
        doc_filename = conv_res.input.file.stem
        output_files = {}
        
        # Export tables
        for table_ix, table in enumerate(conv_res.document.tables):
            table_df: pd.DataFrame = table.export_to_dataframe(doc=conv_res.document)
            
            # Save CSV
            csv_filename = output_dir / f"{doc_filename}-table-{table_ix + 1}.csv"
            table_df.to_csv(csv_filename, encoding='utf-8')
            output_files[f'csv_{table_ix + 1}'] = str(csv_filename)
            
            # Save HTML
            html_filename = output_dir / f"{doc_filename}-table-{table_ix + 1}.html"
            with html_filename.open("w", encoding='utf-8') as fp:
                fp.write(table.export_to_html(doc=conv_res.document))
            output_files[f'html_{table_ix + 1}'] = str(html_filename)
            
            # Save Markdown
            md_filename = output_dir / f"{doc_filename}-table-{table_ix + 1}.md"
            with md_filename.open("w", encoding='utf-8') as fp:
                fp.write(table_df.to_markdown())
            output_files[f'md_{table_ix + 1}'] = str(md_filename)
        
        # Parse the first HTML table and create JSON output
        html_filename = output_dir / f"{doc_filename}-table-1.html"
        json_result = None

        # List with total time per document
        doc_conversion_secs = conv_res.timings["pipeline_total"].times
        
        if html_filename.exists():
            _log.info("Parsing HTML table and creating JSON output...")
            json_result = parse_html_table_to_json(html_filename, company_name, config)
            
            if json_result:
                # Save JSON output
                json_output_path = output_dir / f"{doc_filename}-financial-data.json"
                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_result, f, indent=2, ensure_ascii=False)
                output_files['json'] = str(json_output_path)
                _log.info(f"Saved JSON output to {json_output_path}")
        
        return {
            "success": True,
            "message": f"Successfully processed document. Found {len(conv_res.document.tables)} table(s).",
            "json_result": json_result,
            "output_files": output_files,
            "processing_time": doc_conversion_secs
        }
        
    except Exception as e:
        _log.error(f"Error processing document: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Error processing document: {str(e)}",
            "json_result": None,
            "output_files": {}
        }


def load_config(config_path: Path = None) -> dict:
    """Load configuration from JSON file."""
    if config_path is None:
        config_path = Path(__file__).parent / "config.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_supported_companies() -> list:
    """Return list of supported company names."""
    return ["BRITANNIA", "COLGATE", "DABUR", "HUL", "ITC", "NESTLE", "P&G"]
