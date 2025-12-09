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


def _find_matching_row(rows: list, labels: list) -> tuple[int, any]:
    """
    Find row matching any of the given labels using fuzzy matching.
    
    Returns:
        Tuple of (row_index, matched_row) or (-1, None)
    """
    for row_index, row in enumerate(rows):
        row_text = row.get_text(separator=' ', strip=True).lower()
        
        for label in labels:
            label_lower = label.lower()
            # Normalize both strings
            row_normalized = re.sub(r'[^\w\s]', '', row_text)
            label_normalized = re.sub(r'[^\w\s]', '', label_lower)
            
            # Check for exact match or fuzzy match
            if label_normalized in row_normalized or row_normalized.startswith(label_normalized[:15]):
                return row_index, row
    
    return -1, None


def parse_html_table_to_json(html_file_path: Path, company_name: str, config: dict, use_fuzzy_matching: bool = True) -> dict:
    """
    Parse HTML table and create JSON output based on config.
    
    Args:
        html_file_path: Path to HTML file containing the table
        company_name: Company name (must match config keys)
        config: Configuration dictionary
        use_fuzzy_matching: If True, use label matching as fallback when tr_number fails
    
    Returns:
        Dictionary with parsed financial data or None on error
    """
    
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
        "financial_data": [],
        "extraction_method": "tr_number"  # Track which method was used
    }
    
    matched_rows_count = 0
    fuzzy_matched_count = 0
    
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
        
        matched_row = None
        
        # Strategy 1: Try tr_number if provided and valid
        if tr_number > 0 and tr_number <= len(rows):
            matched_row = rows[tr_number - 1]  # tr_number is 1-indexed
            matched_rows_count += 1
        
        # Strategy 2: Fallback to fuzzy label matching
        elif use_fuzzy_matching and labels:
            row_index, matched_row = _find_matching_row(rows, labels)
            if matched_row is not None:
                _log.debug(f"Fuzzy matched '{key}' at row {row_index + 1}")
                fuzzy_matched_count += 1
                result["extraction_method"] = "mixed"
        
        # Extract data if row was found
        if matched_row is not None:
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
            _log.warning(f"Could not find row for key: {key} (tr_number: {tr_number}, labels: {labels})")
    
    _log.info(f"Extracted {len(result['financial_data'])} items (tr_number: {matched_rows_count}, fuzzy: {fuzzy_matched_count})")
    return result


def _select_best_table(tables: list, doc_filename: str, output_dir: Path) -> tuple[int, Path]:
    """
    Select the best table from multiple extracted tables based on heuristics.
    
    Returns:
        Tuple of (table_index, html_path) or (0, first_table_path) as fallback
    """
    if not tables:
        return None, None
    
    best_score = -1
    best_index = 0
    
    for table_ix, table in enumerate(tables):
        try:
            html_path = output_dir / f"{doc_filename}-table-{table_ix + 1}.html"
            
            if not html_path.exists():
                continue
            
            # Read and analyze table
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            table_elem = soup.find('table')
            
            if not table_elem:
                continue
            
            rows = table_elem.find_all('tr')
            score = 0
            
            # Heuristic 1: More rows generally better (financial statements are detailed)
            score += min(len(rows), 50) * 2
            
            # Heuristic 2: Check for financial keywords
            table_text = table_elem.get_text().lower()
            financial_keywords = [
                'revenue', 'income', 'expense', 'profit', 'loss', 'tax', 
                'total', 'net', 'eps', 'earnings per share', 'comprehensive',
                'depreciation', 'amortisation', 'finance cost'
            ]
            
            for keyword in financial_keywords:
                if keyword in table_text:
                    score += 10
            
            # Heuristic 3: Has numeric columns (financial data should have numbers)
            has_numbers = bool(re.search(r'\d+[,.]?\d*', table_text))
            if has_numbers:
                score += 20
            
            # Heuristic 4: Penalty for very small tables (likely not the main statement)
            if len(rows) < 10:
                score -= 30
            
            _log.debug(f"Table {table_ix + 1} score: {score} (rows: {len(rows)})")
            
            if score > best_score:
                best_score = score
                best_index = table_ix
                
        except Exception as e:
            _log.warning(f"Error analyzing table {table_ix + 1}: {e}")
            continue
    
    best_html_path = output_dir / f"{doc_filename}-table-{best_index + 1}.html"
    _log.info(f"Selected table {best_index + 1} with score {best_score}")
    return best_index, best_html_path


def process_pdf_document(pdf_path: Path, company_name: str, output_dir: Path, config: dict, 
                         prefer_standalone: bool = True, use_fuzzy_matching: bool = True) -> dict:
    """
    Optimized function to process PDF documents with multiple format support.
    
    Args:
        pdf_path: Path to the PDF file
        company_name: Name of the company (must match config keys)
        output_dir: Directory to save output files
        config: Configuration dictionary with parsing rules
        prefer_standalone: Prefer standalone over consolidated statements
        use_fuzzy_matching: Enable fuzzy label matching as fallback
    
    Returns:
        Dictionary with:
        - success: bool
        - message: str
        - json_result: dict (if successful)
        - output_files: dict of generated file paths
        - processing_time: float (seconds)
        - table_info: dict with table selection details
    """
    try:
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find target page
        target_page = find_target_page(pdf_path)
        
        page_range = None
        if target_page is not None:
            _log.info(f"Target page identified: {target_page + 1}")
            # Try target page first, but allow fallback to full document
            page_range = (target_page + 1, target_page + 1)
        else:
            _log.warning("No specific target page found. Will process entire document and select best table.")
        
        # Configure accelerator (optimized settings)
        accelerator_options = AcceleratorOptions(
            num_threads=8, device=AcceleratorDevice.CPU
        )
        
        # Configure pipeline with adaptive settings
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
        
        # Convert document with retry logic
        conv_res = None
        retry_count = 0
        max_retries = 2
        
        while retry_count <= max_retries and conv_res is None:
            try:
                if page_range:
                    _log.info(f"Converting page {page_range[0]} (attempt {retry_count + 1})")
                    conv_res = doc_converter.convert(pdf_path, page_range=page_range)
                else:
                    _log.info(f"Converting entire document (attempt {retry_count + 1})")
                    conv_res = doc_converter.convert(pdf_path)
                    
            except Exception as conv_error:
                retry_count += 1
                if retry_count > max_retries:
                    raise
                _log.warning(f"Conversion attempt {retry_count} failed: {conv_error}. Retrying...")
                
                # On retry, try full document if single page failed
                if page_range is not None:
                    _log.info("Falling back to full document conversion")
                    page_range = None
        
        doc_filename = conv_res.input.file.stem
        output_files = {}
        table_info = {
            "total_tables": len(conv_res.document.tables),
            "selected_table": 1,
            "selection_method": "default"
        }
        
        # Export all tables
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
        
        # Smart table selection for JSON parsing
        json_result = None
        selected_html = None
        
        if len(conv_res.document.tables) > 1:
            # Multiple tables: use heuristics to select best one
            _log.info(f"Found {len(conv_res.document.tables)} tables. Selecting best match...")
            best_table_ix, selected_html = _select_best_table(
                conv_res.document.tables, doc_filename, output_dir
            )
            if selected_html:
                table_info["selected_table"] = best_table_ix + 1
                table_info["selection_method"] = "heuristic"
        elif len(conv_res.document.tables) == 1:
            # Single table: use it
            selected_html = output_dir / f"{doc_filename}-table-1.html"
            table_info["selection_method"] = "single_table"
        
        # Get processing time
        doc_conversion_secs = conv_res.timings["pipeline_total"].times
        
        # Parse selected table and create JSON output
        if selected_html and selected_html.exists():
            _log.info(f"Parsing table {table_info['selected_table']} and creating JSON output...")
            json_result = parse_html_table_to_json(
                selected_html, company_name, config, use_fuzzy_matching=use_fuzzy_matching
            )
            
            if json_result:
                # Add metadata to JSON result
                json_result["metadata"] = {
                    "source_file": pdf_path.name,
                    "table_number": table_info["selected_table"],
                    "total_tables": table_info["total_tables"],
                    "extraction_method": json_result.get("extraction_method", "unknown"),
                    "processing_time_seconds": doc_conversion_secs
                }
                
                # Save JSON output
                json_output_path = output_dir / f"{doc_filename}-financial-data.json"
                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_result, f, indent=2, ensure_ascii=False)
                output_files['json'] = str(json_output_path)
                _log.info(f"Saved JSON output to {json_output_path}")
        
        return {
            "success": True,
            "message": f"Successfully processed document. Found {table_info['total_tables']} table(s), selected table {table_info['selected_table']}.",
            "json_result": json_result,
            "output_files": output_files,
            "processing_time": doc_conversion_secs,
            "table_info": table_info
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
