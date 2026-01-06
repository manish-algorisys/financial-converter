"""
AI-Powered Financial Data Extractor using OpenAI
Extracts financial data from HTML/Markdown tables using GPT models
"""
import os
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
import openai
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

_log = logging.getLogger(__name__)


class AIFinancialExtractor:
    """Extract financial data from parsed documents using OpenAI."""
    
    # System prompt for financial data extraction (template-aware)
    SYSTEM_PROMPT = """You are an expert financial data extraction AI. Extract COMPLETE financial data from quarterly/annual financial statements.

**OUTPUT FORMAT:**
```json
{{
  "company_name": "COMPANY_NAME",
  "financial_data": [
    {{
      "particular": "Sale of goods",
      "key": "sale_of_goods",
      "values": {{
        "30.06.2025": "4,357.64",
        "30.06.2024": "3,892.15",
        "31.03.2025": "15,678.90",
        "31.03.2025_Y": "16,859.22"
      }}
    }}
  ]
}}
```

**METRIC CATEGORIES & KEYS:**

Revenue (Operating):
• sale_of_goods, export_sales, service_revenue, other_operating_revenues
• revenue_from_operations = SUM(above) - EXCLUDING other_income

Revenue (Non-Operating):
• other_income - SEPARATE from operations (interest, dividends, gains)
• total_income = revenue_from_operations + other_income

Expenses:
• cost_of_materials_consumed, excise_duty, purchases_stock_in_trade, changes_in_inventories
• employee_benefits_expense, finance_costs, depreciation_amortisation_expense
• other_expense, advertising_expense, impairment_losses, total_expenses

Profit & Tax:
• profit_before_exceptional_and_tax, exceptional_item_expense, profit_before_tax
• current_tax, deferred_tax, total_tax_expense, net_profit

Other:
• other_comprehensive_income, total_comprehensive_income
• paid_up_equity_share_capital, other_equity, eps_basic, eps_diluted

**PERIOD KEY FORMAT - CRITICAL:**
Period keys in "values" object MUST be in DD.MM.YYYY format. DO NOT use table header text!

✗ WRONG (table header text):
  "Quarter Ended (Unaudited)": "1,42,064"
  "Quarter Ended March 31,2025 (Audited)": "1,45,202"
  "Year Ended March 31,2025 (Audited)": "5,99,920"

✓ CORRECT (extracted dates):
  "30.06.2025": "1,42,064"      ← Quarterly (Q1 FY2026)
  "31.03.2025": "1,45,202"      ← Quarterly (Q4 FY2025)
  "30.06.2024": "1,48,576"      ← Quarterly (Q1 FY2025)
  "31.03.2025_Y": "5,99,920"    ← Yearly (FY2025) - note "_Y" suffix

**HOW TO EXTRACT DATES:**
- "Quarter Ended June 30, 2025" → "30.06.2025"
- "Quarter Ended March 31, 2025" → "31.03.2025"
- "Year Ended March 31, 2025" → "31.03.2025_Y" (add "_Y" for yearly)
- "Q1 FY2026" → "30.06.2025" (Q1 = Jun 30)
- "FY 2025" → "31.03.2025_Y" (fiscal year ends Mar 31)

**OTHER EXTRACTION RULES:**
1. Numbers: Keep commas - "4,357.64" not "4357.64"
2. Negatives: Brackets "(123.45)" or minus "-123.45"
3. Missing Values: Use empty string ""
4. Extract ALL rows and ALL periods - no skipping

**CRITICAL:** Return ONLY valid JSON. No explanatory text."""

    # System prompt WITH template metrics (used when template is provided)
    SYSTEM_PROMPT_WITH_TEMPLATE = """You are an expert financial data extraction AI. Extract COMPLETE financial data from quarterly/annual financial statements.

**CRITICAL: Extract ALL date columns/periods found in the table - NOT just 2 periods!**

**STEP 1: IDENTIFY ALL DATE COLUMNS**
First, scan the table header and identify EVERY date column (e.g., 30.06.2025, 30.06.2024, 31.03.2025, 31.12.2024).
Tables typically have 3-4+ periods. Extract values for ALL of them.

**STEP 2: EXTRACT FOR REQUIRED METRICS**
You will receive a list of required metrics from the Excel template.
For EACH metric, extract values for ALL periods identified in Step 1.

REQUIRED METRICS:
{template_metrics}

**OUTPUT FORMAT:**
```json
{{
  "company_name": "COMPANY_NAME",
  "financial_data": [
    {{
      "particular": "Sale of goods",
      "key": "sale_of_goods",
      "values": {{
        "30.06.2025": "4,357.64",
        "30.06.2024": "3,892.15",
        "31.03.2025": "15,678.90",
        "31.03.2025_Y": "16,859.22"
      }}
    }}
  ]
}}
```

**MATCHING STRATEGY:**
✓ GOOD MATCHES (accept these):
  "Cost of material consumed" ≈ "Cost of materials consumed"
  "Employee benefit expense" ≈ "Employee benefits expense"  
  "PBT" ≈ "Profit before tax"

✓ MATCH CRITERIA (priority order):
  1. Exact match (case-insensitive)
  2. Partial word match
  3. Synonym match (PBT = Profit Before Tax)
  4. Abbreviation match (singular/plural)
  5. Semantic similarity (>75%)

**PERIOD KEY FORMAT - CRITICAL:**
Period keys in "values" object MUST be in DD.MM.YYYY format. DO NOT use table header text!

✗ WRONG (table header text):
  {{"Quarter Ended (Unaudited)": "1,42,064"}}
  {{"Quarter Ended March 31,2025 (Audited)": "1,45,202"}}

✓ CORRECT (extracted dates):
  {{"30.06.2025": "1,42,064", "31.03.2025": "1,45,202", "31.03.2025_Y": "5,99,920"}}

**HOW TO EXTRACT DATES FROM HEADERS:**
- "Quarter Ended June 30, 2025 (Unaudited)" → "30.06.2025"
- "Quarter Ended March 31, 2025 (Audited)" → "31.03.2025" 
- "Year Ended March 31, 2025" → "31.03.2025_Y" (add "_Y" for yearly!)
- "Q1 FY2026" → "30.06.2025"
- "FY 2025" → "31.03.2025_Y"

**OTHER EXTRACTION RULES:**
1. Numbers: Keep commas - "4,357.64" not "4357.64"
2. Negatives: Brackets "(123.45)" or minus "-123.45"
3. Missing Values: Use empty string ""
4. Extract ALL periods found in table header - minimum 3-4 periods
5. If metric in template but not in table → include with empty values {{}}

**CRITICAL:** Return ONLY valid JSON. No explanatory text."""

    USER_PROMPT_TEMPLATE = """Extract ALL financial data from this {format} table for {company_name}:

{content}

Return ONLY the JSON object. No additional text."""

    USER_PROMPT_WITH_TEMPLATE = """Extract financial data from this {format} table for {company_name}.

**IMPORTANT:** 
1. First identify ALL date columns in the table header (typically 3-4+ periods)
2. Extract values for EVERY metric (from system prompt) across ALL periods
3. Do NOT skip any date columns - extract complete data

TABLE CONTENT:
{content}

Return ONLY the JSON object with ALL periods. No explanations."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize AI extractor.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        _log.info(f"Initialized AIFinancialExtractor with model: {model}")
    
    def _read_file_content(self, file_path: Path) -> str:
        """Read content from HTML or Markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            _log.error(f"Error reading file {file_path}: {str(e)}")
            raise
    
    def _clean_json_response(self, response: str) -> str:
        """Clean OpenAI response to extract valid JSON."""
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        elif response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
        return response.strip()
    
    def _read_template_metrics(self, template_excel_path: Path) -> List[str]:
        """
        Read metric names from Excel template (Column A, starting from row 3).
        
        Args:
            template_excel_path: Path to Excel template file
        
        Returns:
            List of metric strings like "Sale of goods (key: sale_of_goods)"
        """
        try:
            from openpyxl import load_workbook
            
            wb = load_workbook(template_excel_path, data_only=True)
            ws = wb.active
            
            metrics = []
            # Start from row 3 (rows 1-2 are usually headers)
            for row_idx in range(3, ws.max_row + 1):
                cell = ws.cell(row=row_idx, column=1)  # Column A
                if cell.value:
                    metric_name = str(cell.value).strip()
                    # Skip empty cells and section headers (usually uppercase or short)
                    if metric_name and len(metric_name) > 3:
                        # Try to infer key from metric name
                        key = self._infer_key_from_metric(metric_name)
                        metrics.append(f"{metric_name} (key: {key})")
            
            _log.info(f"Read {len(metrics)} metrics from template: {template_excel_path.name}")
            return metrics
            
        except Exception as e:
            _log.warning(f"Failed to read template metrics: {str(e)}")
            return []
    
    def _infer_key_from_metric(self, metric_name: str) -> str:
        """
        Infer standardized key from metric display name.
        
        Args:
            metric_name: Display name like "Sale of Goods"
        
        Returns:
            Inferred key like "sale_of_goods"
        """
        # Convert to lowercase and replace spaces with underscores
        key = metric_name.lower().strip()
        
        # Remove common punctuation
        key = key.replace('(', '').replace(')', '').replace(',', '')
        key = key.replace('&', 'and').replace('-', '_')
        
        # Replace multiple spaces with single underscore
        key = '_'.join(key.split())
        
        # Remove leading/trailing underscores
        key = key.strip('_')
        
        return key
    
    def extract_from_html(self, html_path: Path, company_name: str, 
                         template_excel_path: Path = None) -> Dict:
        """
        Extract financial data from HTML table.
        
        Args:
            html_path: Path to HTML file containing financial table
            company_name: Company name for context
            template_excel_path: Optional Excel template for guided extraction
        
        Returns:
            Dictionary with extracted financial data
        """
        content = self._read_file_content(html_path)
        return self._extract_with_openai(content, company_name, "HTML", template_excel_path)
    
    def extract_from_markdown(self, md_path: Path, company_name: str,
                             template_excel_path: Path = None) -> Dict:
        """
        Extract financial data from Markdown table.
        
        Args:
            md_path: Path to Markdown file containing financial table
            company_name: Company name for context
            template_excel_path: Optional Excel template for guided extraction
        
        Returns:
            Dictionary with extracted financial data
        """
        content = self._read_file_content(md_path)
        return self._extract_with_openai(content, company_name, "Markdown", template_excel_path)
    
    def extract_from_output_dir(self, output_dir: Path, company_name: str, 
                                preferred_format: str = "html", 
                                template_excel_path: Path = None) -> Dict:
        """
        Extract financial data from output directory (tries multiple formats).
        
        Args:
            output_dir: Directory containing parsed output files
            company_name: Company name
            preferred_format: Preferred format to try first ("html" or "markdown")
            template_excel_path: Optional Excel template for guided extraction
        
        Returns:
            Dictionary with extracted financial data
        """
        # Try preferred format first
        if preferred_format == "html":
            html_files = list(output_dir.glob("*-table-*.html"))
            if html_files:
                _log.info(f"Using HTML file: {html_files[0]}")
                return self.extract_from_html(html_files[0], company_name, template_excel_path)
        
        # Try markdown as fallback
        md_files = list(output_dir.glob("*-table-*.md"))
        if md_files:
            _log.info(f"Using Markdown file: {md_files[0]}")
            return self.extract_from_markdown(md_files[0], company_name, template_excel_path)
        
        # Try HTML if markdown was preferred but not found
        if preferred_format == "markdown":
            html_files = list(output_dir.glob("*-table-*.html"))
            if html_files:
                _log.info(f"Falling back to HTML file: {html_files[0]}")
                return self.extract_from_html(html_files[0], company_name, template_excel_path)
        
        raise FileNotFoundError(f"No suitable table files found in {output_dir}")
    
    def _extract_with_openai(self, content: str, company_name: str, format_type: str,
                            template_excel_path: Path = None) -> Dict:
        """
        Extract financial data using OpenAI API.
        
        Args:
            content: HTML or Markdown content
            company_name: Company name
            format_type: "HTML" or "Markdown"
            template_excel_path: Optional Excel template for guided extraction
        
        Returns:
            Extracted financial data dictionary
        """
        try:
            # Truncate content if too long (to stay within token limits)
            max_content_length = 30000  # ~7500 tokens
            if len(content) > max_content_length:
                _log.warning(f"Content truncated from {len(content)} to {max_content_length} chars")
                content = content[:max_content_length]
            
            # Check if template is provided
            template_metrics = []
            if template_excel_path and template_excel_path.exists():
                template_metrics = self._read_template_metrics(template_excel_path)
            
            # Choose appropriate prompts based on template availability
            if template_metrics:
                _log.info(f"Using TEMPLATE-GUIDED extraction with {len(template_metrics)} metrics")
                metrics_text = "\n".join([f"- {m}" for m in template_metrics])
                print(f"Using template with {len(template_metrics)} metrics")
                
                # Use template-aware system prompt with metrics embedded
                system_prompt = self.SYSTEM_PROMPT_WITH_TEMPLATE.format(
                    template_metrics=metrics_text
                )
                user_prompt = self.USER_PROMPT_WITH_TEMPLATE.format(
                    format=format_type,
                    company_name=company_name,
                    content=content
                )
            else:
                _log.info("Using STANDARD extraction (no template)")
                system_prompt = self.SYSTEM_PROMPT
                user_prompt = self.USER_PROMPT_TEMPLATE.format(
                    format=format_type,
                    company_name=company_name,
                    content=content
                )
            
            _log.info(f"Sending request to OpenAI ({self.model})...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            # Extract JSON from response
            json_str = response.choices[0].message.content
            json_str = self._clean_json_response(json_str)
            
            _log.info(f"Received response from OpenAI (tokens used: {response.usage.total_tokens})")
            
            # Parse and validate JSON
            data = json.loads(json_str)
            
            # Validate structure
            if 'financial_data' not in data:
                raise ValueError("Response missing 'financial_data' key")
            
            # Add extraction metadata
            data['metadata'] = {
                'extraction_method': 'openai',
                'model': self.model,
                'tokens_used': response.usage.total_tokens,
                'source_format': format_type.lower(),
                'template_guided': bool(template_metrics),
                'template_metrics_count': len(template_metrics)
            }
            
            _log.info(f"Successfully extracted {len(data['financial_data'])} financial items")
            return data
            
        except json.JSONDecodeError as e:
            _log.error(f"Failed to parse JSON response: {str(e)}")
            _log.error(f"Raw response: {json_str[:500]}...")
            raise ValueError(f"Invalid JSON response from OpenAI: {str(e)}")
        except Exception as e:
            _log.error(f"Error during OpenAI extraction: {str(e)}", exc_info=True)
            raise


def validate_financial_data(data: Dict) -> bool:
    """
    Validate extracted financial data structure.
    
    Args:
        data: Extracted financial data dictionary
    
    Returns:
        True if valid, raises ValueError otherwise
    """
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")
    
    if 'company_name' not in data:
        raise ValueError("Missing 'company_name' key")
    
    if 'financial_data' not in data:
        raise ValueError("Missing 'financial_data' key")
    
    if not isinstance(data['financial_data'], list):
        raise ValueError("'financial_data' must be a list")
    
    # Validate each financial item
    for i, item in enumerate(data['financial_data']):
        if not isinstance(item, dict):
            raise ValueError(f"Item {i} is not a dictionary")
        
        required_keys = ['particular', 'key', 'values']
        for key in required_keys:
            if key not in item:
                raise ValueError(f"Item {i} missing required key: {key}")
        
        if not isinstance(item['values'], dict):
            raise ValueError(f"Item {i} 'values' must be a dictionary")
    
    return True
