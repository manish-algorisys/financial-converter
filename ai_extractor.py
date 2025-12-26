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
    
    # System prompt for financial data extraction
    SYSTEM_PROMPT = """You are a financial data extraction specialist. Your task is to extract COMPLETE structured financial data from quarterly financial statements.

EXTRACT EVERY SINGLE ROW from the table with their values for ALL periods:

**Revenue Section:**
- Sale of goods (key: "sale_of_goods")
- Export sales (key: "export_sales")
- Service revenue (key: "service_revenue")
- Other operating revenues (key: "other_operating_revenues")
- Total revenue from operations (key: "revenue_from_operations")
- Other income (key: "other_income")
- Total income (key: "total_income")

**Expenses Section:**
- Cost of materials consumed (key: "cost_of_materials_consumed")
- Excise duty (key: "excise_duty")
- Purchases of stock-in-trade (key: "purchases_stock_in_trade")
- Changes in inventories (key: "changes_in_inventories")
- Employee benefits expense (key: "employee_benefits_expense")
- Finance costs (key: "finance_costs")
- Depreciation and amortisation expense (key: "depreciation_amortisation_expense")
- Other expenses (key: "other_expense")
- Advertising expense (key: "advertising_expense")
- Impairment losses (key: "impairment_losses")
- Total expenses (key: "total_expenses")

**Profit & Tax Section:**
- Profit before exceptional items and tax (key: "profit_before_exceptional_and_tax")
- Exceptional items (key: "exceptional_item_expense")
- Profit before tax (key: "profit_before_tax")
- Current tax (key: "current_tax")
- Deferred tax (key: "deferred_tax")
- Total tax expense (key: "total_tax_expense")
- Net profit (key: "net_profit")

**Other Comprehensive Income:**
- OCI non-reclassifiable items (key: "oci_non_reclass_items")
- Tax on OCI items (key: "tax_on_non_reclass_items")
- Other comprehensive income (key: "other_comprehensive_income")
- Total comprehensive income (key: "total_comprehensive_income")

**Equity & EPS:**
- Paid-up equity share capital (key: "paid_up_equity_share_capital")
- Other equity (key: "other_equity")
- EPS basic (key: "eps_basic")
- EPS diluted (key: "eps_diluted")

Return ONLY a valid JSON object:
{
  "company_name": "COMPANY_NAME",
  "financial_data": [
    {
      "particular": "Sale of goods",
      "key": "sale_of_goods",
      "values": {
        "30.06.2025": "4,357.64",
        "31.03.2025": "4,218.90",
        "30.06.2024": "3,967.38",
        "31.03.2025_Y": "16,859.22"
      }
    }
  ]
}

CRITICAL RULES:
- Extract EVERY ROW from the table - do NOT skip any rows
- Extract ALL PERIODS/COLUMNS - do not skip any date columns
- Use standard date formats: DD.MM.YYYY (e.g., "30.06.2025")
- For yearly/annual periods (look for "YEAR ENDED", "FY", "12M" headers), append "_Y" suffix (e.g., "31.03.2025_Y")
- Keep commas in numbers: "4,357.64" not "4357.64"
- Negative values: use brackets "(123.45)" or minus "-123.45"
- Use EXACT key names from the list above - consistency is critical
- If a value is not available for a specific period, use empty string ""
- Do NOT include any explanatory text outside the JSON"""

    USER_PROMPT_TEMPLATE = """Extract financial data from this {format} table for {company_name}:

{content}

Extract all financial metrics with values for all available periods. Return ONLY the JSON object, no additional text."""

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
    
    def extract_from_html(self, html_path: Path, company_name: str) -> Dict:
        """
        Extract financial data from HTML table.
        
        Args:
            html_path: Path to HTML file containing financial table
            company_name: Company name for context
        
        Returns:
            Dictionary with extracted financial data
        """
        content = self._read_file_content(html_path)
        return self._extract_with_openai(content, company_name, "HTML")
    
    def extract_from_markdown(self, md_path: Path, company_name: str) -> Dict:
        """
        Extract financial data from Markdown table.
        
        Args:
            md_path: Path to Markdown file containing financial table
            company_name: Company name for context
        
        Returns:
            Dictionary with extracted financial data
        """
        content = self._read_file_content(md_path)
        return self._extract_with_openai(content, company_name, "Markdown")
    
    def extract_from_output_dir(self, output_dir: Path, company_name: str, 
                                preferred_format: str = "html") -> Dict:
        """
        Extract financial data from output directory (tries multiple formats).
        
        Args:
            output_dir: Directory containing parsed output files
            company_name: Company name
            preferred_format: Preferred format to try first ("html" or "markdown")
        
        Returns:
            Dictionary with extracted financial data
        """
        # Try preferred format first
        if preferred_format == "html":
            html_files = list(output_dir.glob("*-table-*.html"))
            if html_files:
                _log.info(f"Using HTML file: {html_files[0]}")
                return self.extract_from_html(html_files[0], company_name)
        
        # Try markdown as fallback
        md_files = list(output_dir.glob("*-table-*.md"))
        if md_files:
            _log.info(f"Using Markdown file: {md_files[0]}")
            return self.extract_from_markdown(md_files[0], company_name)
        
        # Try HTML if markdown was preferred but not found
        if preferred_format == "markdown":
            html_files = list(output_dir.glob("*-table-*.html"))
            if html_files:
                _log.info(f"Falling back to HTML file: {html_files[0]}")
                return self.extract_from_html(html_files[0], company_name)
        
        raise FileNotFoundError(f"No suitable table files found in {output_dir}")
    
    def _extract_with_openai(self, content: str, company_name: str, format_type: str) -> Dict:
        """
        Extract financial data using OpenAI API.
        
        Args:
            content: HTML or Markdown content
            company_name: Company name
            format_type: "HTML" or "Markdown"
        
        Returns:
            Extracted financial data dictionary
        """
        try:
            # Truncate content if too long (to stay within token limits)
            max_content_length = 30000  # ~7500 tokens
            if len(content) > max_content_length:
                _log.warning(f"Content truncated from {len(content)} to {max_content_length} chars")
                content = content[:max_content_length]
            
            user_prompt = self.USER_PROMPT_TEMPLATE.format(
                format=format_type,
                company_name=company_name,
                content=content
            )
            
            _log.info(f"Sending request to OpenAI ({self.model})...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
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
                'source_format': format_type.lower()
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
