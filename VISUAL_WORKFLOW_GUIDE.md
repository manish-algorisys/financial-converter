# Visual Workflow Guide - PDF Parser & Excel Generation

Complete visual guide to understanding the financial document parser system with both config-driven and AI-powered approaches.

## Table of Contents

- [System Overview](#system-overview)
- [Approach Comparison](#approach-comparison)
- [Config-Driven Workflow](#config-driven-workflow)
- [AI-Powered Workflow](#ai-powered-workflow)
- [Decision Tree](#decision-tree)
- [File Flow Diagrams](#file-flow-diagrams)
- [API Call Sequences](#api-call-sequences)
- [Streamlit UI Workflow](#streamlit-ui-workflow-ai-excel-generator-tab)
- [Architecture Components](#architecture-components)
- [Error Handling Flows](#error-handling-flows)
- [Performance Optimization](#performance-optimization)
- [Best Practices Summary](#best-practices-summary)
- [Edge Cases & Limitations](#edge-cases--limitations)
- [Quick Reference](#quick-reference)

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FINANCIAL DOCUMENT PARSER SYSTEM                     │
│                            v2.3 (January 2026)                          │
│  Input: PDF Financial Reports → Output: Structured Excel/CSV/JSON       │
└─────────────────────────────────────────────────────────────────────────┘

                            ▼ TWO APPROACHES ▼

        ┌──────────────────────────┐              ┌──────────────────────┐
        │  CONFIG-DRIVEN (v2.1)    │              │  AI-POWERED (v2.2)   │
        │                          │              │                      │
        │  ✓ Fast & Free          │               │  ✓ Universal         │
        │  ✓ Accurate             │               │  ✓ Zero-Config       │
        │  ✗ Needs Config         │               │  ✗ Costs $0.002     │
        └──────────────────────────┘              └──────────────────────┘
                 │                                      │
                 └──────────────┬───────────────────────┘
                                ▼
                    ┌───────────────────────┐
                    │   EXCEL/CSV OUTPUT    │
                    │   Indian Formatting   │
                    │   Multi-Company (v2.3)│  ← NEW
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   FILE MANAGEMENT     │
                    │   • Save to Storage   │  ← NEW v2.3
                    │   • Saved Files Tab   │
                    │   • Metadata Tracking │
                    └───────────────────────┘
```

---

## Approach Comparison

### Visual Comparison Matrix

```
┌─────────────────────────┬─────────────────────┬─────────────────────┐
│      FEATURE            │   CONFIG-DRIVEN     │    AI-POWERED       │
├─────────────────────────┼─────────────────────┼─────────────────────┤
│ Speed                   │ ⚡⚡⚡ 5-15 sec      │ ⚡⚡ 10-20 sec    │
│ Cost                    │ 💰 FREE             │ 💰 $0.001-$0.003    │
│ Accuracy                │ 📊 95-99%           │ 📊 90-95%           │
│ Setup Required          │ ⚙️ Config needed    │ ✅ None             │
│ New Companies           │ ❌ Need config      │ ✅ Works instantly  │
│ Format Variations       │ ⚠️ May fail         │ ✅ Adaptive         │
│ Supported Companies     │ 7 companies         │ ♾️ Any company      │
│ Internet Required       │ ❌ No               │ ✅ Yes (OpenAI)     │
│ API Key Required        │ ❌ No               │ ✅ OPENAI_API_KEY   │
└─────────────────────────┴─────────────────────┴─────────────────────┘
```

### When to Use Each Approach

```
START: Need to extract financial data
  │
  ├─ Is company in config.json?
  │  │
  │  ├─ YES ─→ Use CONFIG-DRIVEN
  │  │         • Fastest option
  │  │         • Zero cost
  │  │         • Best accuracy
  │  │
  │  └─ NO ──→ Use AI-POWERED
  │            • Works with any format
  │            • No configuration needed
  │            • Small cost (~$0.002)
  │
  └─ Is PDF format unusual/custom?
     │
     └─ YES ─→ Use AI-POWERED
               • Handles variations better
               • Adaptive to different layouts
```

---

## Config-Driven Workflow

### Complete Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                    CONFIG-DRIVEN EXTRACTION FLOW                     │
└──────────────────────────────────────────────────────────────────────┘

STEP 1: PDF UPLOAD & PAGE DETECTION
───────────────────────────────────
┌─────────────┐
│ PDF Upload  │ (Financial Report - any company with config)
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  Page Detection Logic   │
│                         │
│  Priority 1:            │
│  → "standalone" keyword │
│                         │
│  Priority 2:            │
│  → Generic patterns     │
│    + NO "consolidated"  │
│                         │
│  Priority 3:            │
│  → Any financial page   │
└──────────┬──────────────┘
           │
           ▼
    ┌──────────────┐
    │ Target Page  │ (e.g., Page 3)
    └──────┬───────┘


STEP 2: TABLE EXTRACTION (DOCLING)
───────────────────────────────────
           │
           ▼
    ┌─────────────────┐
    │  Docling Engine │
    │                 │
    │  • OCR enabled  │
    │  • Table Former │
    │  • Cell Matching│
    └────────┬────────┘
             │
             ├─── Multiple Tables Found? ───┐
             │                              │
             ▼                              ▼
    ┌────────────────┐            ┌───────────────────┐
    │ Single Table   │            │ Score Each Table  │
    └────────┬───────┘            │                   │
             │                    │ Score = f(rows,   │
             │                    │   keywords,       │
             │                    │   numbers)        │
             │                    └────────┬──────────┘
             │                             │
             └────────────┬────────────────┘
                          ▼
                 ┌──────────────────┐
                 │  Best Table      │
                 │  Selected        │
                 └────────┬─────────┘


STEP 3: FILE GENERATION
───────────────────────
                          │
                          ├────────────────┬────────────────┐
                          ▼                ▼                ▼
                    ┌─────────┐    ┌──────────┐    ┌──────────┐
                    │  .html  │    │   .md    │    │   .csv   │
                    └─────────┘    └──────────┘    └──────────┘
                          │                │                │
                          └────────┬───────┴────────────────┘
                                   ▼
                         ┌───────────────────┐
                         │ Save to output/   │
                         │ {COMPANY}_{DOC}/  │
                         └─────────┬─────────┘


STEP 4: CONFIG-BASED PARSING
─────────────────────────────
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │  Load config.json        │
                    │                          │
                    │  Company Config:         │
                    │  • column_layout         │
                    │  • financial_data[]      │
                    │    - key                 │
                    │    - labels[]            │
                    │    - tr_number           │
                    └──────────┬───────────────┘
                               │
                               ▼
                ┌────────────────────────────────┐
                │  Parse HTML with BeautifulSoup │
                └──────────┬─────────────────────┘
                           │
                           ▼
            ┌──────────────────────────────────┐
            │  Dual Extraction Strategy:       │
            │                                  │
            │  PRIMARY:                        │
            │  → Use tr_number (row index)     │
            │    Fast & Direct                 │
            │                                  │
            │  FALLBACK:                       │
            │  → Fuzzy label matching          │
            │    Find row by text similarity   │
            └──────────┬───────────────────────┘
                       │
                       ▼
            ┌──────────────────────────┐
            │ Extract all 30+ metrics  │
            │ for all periods          │
            └──────────┬───────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  financial-data.json │
            │                      │
            │  {                   │
            │    "30.06.2025": {   │
            │      "sale_of_goods":│
            │         4357.64,     │
            │      ...             │
            │    }                 │
            │  }                   │
            └──────────┬───────────┘


STEP 5: EXCEL GENERATION
─────────────────────────
                       │
                       ▼
         ┌──────────────────────────┐
         │ FinancialExcelGenerator  │
         │                          │
         │ • Map JSON → 47 rows     │
         │ • Apply styling          │
         │ • Indian number format   │
         │ • Bracket negatives      │
         └──────────┬───────────────┘
                    │
                    ▼
         ┌────────────────────┐
         │  statement.xlsx    │
         │                    │
         │  Professional      │
         │  47-row format     │
         │  All periods       │
         └────────────────────┘


PERFORMANCE METRICS
───────────────────
Total Time: 5-15 seconds
├─ Page Detection: 0.5-1s
├─ Table Extraction: 3-10s
├─ Parsing: 0.5-1s
└─ Excel Generation: 1-3s

Cost: $0.00 (FREE)
Accuracy: 95-99%
```

### Example: Britannia Q2 2025

```
INPUT: Britannia_Unaudited_Q2_June_2026.pdf (2.3 MB, 8 pages)
  │
  ▼ Page Detection (0.8s)
  │
Found: Page 3 - "STANDALONE UNAUDITED FINANCIAL RESULTS"
  │
  ▼ Docling Extraction (8.2s)
  │
3 tables found → Score: [85, 42, 23] → Select Table 1
  │
  ▼ Files Created
  │
output/BRITANNIA_Britannia_Unaudited_Q2_June_2026/
  ├─ Britannia_Unaudited_Q2_June_2026-table-1.html
  ├─ Britannia_Unaudited_Q2_June_2026-table-1.md
  ├─ Britannia_Unaudited_Q2_June_2026-table-1.csv
  └─ Britannia_Unaudited_Q2_June_2026-financial-data.json
  │
  ▼ Config Parsing (0.6s)
  │
config.json → britannia → 35 metrics extracted
Extraction Method: tr_number (28), fuzzy (7)
  │
  ▼ Excel Generation (2.1s)
  │
OUTPUT: statement.xlsx (45 KB)
  ├─ 47 rows × 11 columns
  ├─ 4 periods with data (B, C, D, G)
  └─ 7 empty columns (E, F, H-L)

Total Time: 11.7 seconds
Cost: $0.00
```

---

## AI-Powered Workflow

### Complete Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                     AI-POWERED EXTRACTION FLOW                       │
└──────────────────────────────────────────────────────────────────────┘

STEP 1: PDF UPLOAD & TABLE EXTRACTION (SAME AS CONFIG-DRIVEN)
──────────────────────────────────────────────────────────────
┌─────────────┐
│ PDF Upload  │ (Any financial report - even unknown companies)
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Page Detection   │ (Multi-priority logic)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Docling Extract  │ (OCR + Table Former)
└────────┬─────────┘
         │
         ▼
┌───────────────────────────────────────┐
│ Save Intermediate Files:              │
│                                       │
│ ✓ .html  ← Primary source for AI      │
│ ✓ .md    ← Fallback source            │
│ ✓ .csv   ← For reference              │
└────────┬──────────────────────────────┘


STEP 2: AI EXTRACTION REQUEST
──────────────────────────────
         │
         ▼
┌──────────────────────────────┐
│ /api/generate-excel-ai       │
│                              │
│ Request Body:                │
│ {                            │
│   "company_name": "X",       │
│   "document_name": "Y",      │
│   "preferred_format": "html" │
│ }                            │
└────────┬─────────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Load HTML/MD from disk  │
│                         │
│ Priority:               │
│ 1. Try HTML first       │
│ 2. Fallback to MD       │
└────────┬────────────────┘


STEP 3: OPENAI PROCESSING
──────────────────────────
         │
         ▼
┌────────────────────────────────────────────────────────────────┐
│              OpenAI GPT-4o-mini Extraction                     │
│                                                                │
│  SYSTEM PROMPT:                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ You are a financial data extraction specialist...      │    │
│  │                                                        │    │
│  │ Revenue Section (CRITICAL - Follow Hierarchy):         │    │
│  │ • Sale of goods (key: "sale_of_goods")                 │    │
│  │ • Export sales (key: "export_sales")                   │    │
│  │ • Revenue from operations = sale_of_goods +            │    │
│  │   export_sales + service_revenue +                     │    │
│  │   other_operating_revenues                             │    │
│  │   ⚠️ DO NOT include other_income                       │    │
│  │                                                        │    │
│  │ • Other income (SEPARATE, non-operating)               │    │
│  │ • Total income = revenue_from_operations +             │    │
│  │   other_income                                         │    │
│  │                                                        │    │
│  │ [... 30+ more metrics ...]                             │    │
│  │                                                        │    │
│  │ CRITICAL RULES:                                        │    │
│  │ • Extract EVERY ROW                                    │    │
│  │ • Extract ALL PERIODS/COLUMNS                          │    │
│  │ • Keep commas in numbers: "4,357.64"                   │    │
│  │ • Yearly periods: append "_Y" suffix                   │    │
│  │ • Use EXACT key names                                  │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                │
│  USER PROMPT:                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Extract financial data from this HTML table for        │    │
│  │ COMPANY_NAME:                                          │    │
│  │                                                        │    │
│  │ [HTML TABLE CONTENT - truncated to ~30KB]              │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                │
│  API Call:                                                     │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ client.chat.completions.create(                        │    │
│  │   model="gpt-4o-mini",                                 │    │
│  │   messages=[{system}, {user}],                         │    │
│  │   temperature=0.1,  # Low for consistency              │    │
│  │   response_format={"type": "json_object"}              │    │
│  │ )                                                      │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                │
│  Response Time: 2-5 seconds                                    │
│  Tokens Used: 3,000-5,000                                      │
│  Cost: ~$0.002 per request                                     │
└───────────────────────────┬────────────────────────────────────┘
                            │
                            ▼
                ┌────────────────────────┐
                │   OpenAI Response      │
                │                        │
                │   JSON Structure:      │
                │   {                    │
                │     "company_name": "X"│
                │     "financial_data": [│
                │       {                │
                │         "particular": "│
                │         "key": "...",  │
                │         "values": {    │
                │           "30.06.2025":│
                │             "4,357.64" │
                │         }              │
                │       }                │
                │     ]                  │
                │   }                    │
                └────────┬───────────────┘


STEP 4: JSON VALIDATION & TRANSFORMATION
─────────────────────────────────────────
                            │
                            ▼
                ┌───────────────────────────┐
                │  Validate Structure       │
                │                           │
                │  ✓ Has company_name       │
                │  ✓ Has financial_data[]   │
                │  ✓ Each item has:         │
                │    - particular           │
                │    - key                  │
                │    - values{}             │
                └────────┬──────────────────┘
                         │
                         ▼
                ┌────────────────────────────┐
                │ Transform to Excel Format  │
                │                            │
                │ financial_data[] →         │
                │ {                          │
                │   "30.06.2025": {          │
                │     "sale_of_goods": val   │
                │   }                        │
                │ }                          │
                └────────┬───────────────────┘
                         │
                         ▼
                ┌─────────────────────┐
                │ Add AI Metadata     │
                │                     │
                │ {                   │
                │   extraction_method:│
                │     "openai",       │
                │   model:            │
                │     "gpt-4o-mini",  │
                │   tokens_used: 3500 │
                │ }                   │
                └────────┬────────────┘


STEP 5: EXCEL GENERATION (SAME AS CONFIG-DRIVEN)
─────────────────────────────────────────────────
                         │
                         ▼
         ┌──────────────────────────┐
         │ FinancialExcelGenerator  │
         │                          │
         │ • Map JSON → 47 rows     │
         │ • Apply styling          │
         │ • Indian number format   │
         │ • Bracket negatives      │
         └──────────┬───────────────┘
                    │
                    ▼
         ┌────────────────────┐
         │  statement.xlsx    │
         │                    │
         │  Professional      │
         │  47-row format     │
         │  All periods       │
         └────────────────────┘
              │
              ├─ Response Headers:
              │  X-Extraction-Method: openai
              │  X-Model: gpt-4o-mini
              │  X-Tokens-Used: 3500
              │  X-Processing-Time: 3.2s


PERFORMANCE METRICS
───────────────────
Total Time: 10-20 seconds
├─ Page Detection: 0.5-1s
├─ Table Extraction: 3-10s
├─ AI Processing: 2-5s
└─ Excel Generation: 1-3s

Cost: $0.001-$0.003
Accuracy: 90-95%
Flexibility: ∞ (works with any format)
```

### Example: Unknown Company Report

```
INPUT: NewCompany_Q1_2025.pdf (1.8 MB, 12 pages)
  │
  ▼ Page Detection (1.1s)
  │
Found: Page 5 - "UNAUDITED FINANCIAL RESULTS"
  │
  ▼ Docling Extraction (7.5s)
  │
1 table found → Auto-select Table 1
  │
  ▼ Files Created
  │
output/NEWCOMPANY_NewCompany_Q1_2025/
  ├─ NewCompany_Q1_2025-table-1.html  ← Used for AI
  ├─ NewCompany_Q1_2025-table-1.md
  └─ NewCompany_Q1_2025-table-1.csv
  │
  ▼ AI Extraction Request
  │
POST /api/generate-excel-ai
{
  "company_name": "NEWCOMPANY",
  "document_name": "NEWCOMPANY_NewCompany_Q1_2025",
  "preferred_format": "html"
}
  │
  ▼ Load HTML (0.1s)
  │
HTML content: 28,450 bytes (within 30KB limit)
  │
  ▼ OpenAI API Call (3.8s)
  │
Request → gpt-4o-mini
System Prompt: 8,200 tokens
User Prompt: 4,100 tokens
Total Input: 12,300 tokens
  │
  ▼ Response Received
  │
Output Tokens: 2,800
Total Tokens: 15,100
Cost: $0.00226 (15,100 × $0.15 / 1M)
  │
  ▼ JSON Validation (0.2s)
  │
✓ Structure valid
✓ 32 metrics extracted
✓ 3 periods found: 30.06.2025, 31.03.2025, 31.03.2025_Y
  │
  ▼ Excel Generation (1.9s)
  │
OUTPUT: statement.xlsx (42 KB)
  ├─ 47 rows × 11 columns
  ├─ 3 periods with data (B, C, D)
  └─ 8 empty columns (E-L)

Total Time: 14.6 seconds
Cost: $0.00226
Extraction Method: openai (gpt-4o-mini)
```

---

## Decision Tree

### Choosing the Right Approach

```
                        ┌─────────────────────┐
                        │  START: Need Excel  │
                        │  from PDF Report    │
                        └──────────┬──────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
        ┌──────────────────────┐      ┌──────────────────────┐
        │ Company in config?   │      │ Budget available?    │
        │ (7 supported)        │      │ ($0.002/doc)         │
        └──────┬────────┬──────┘      └──────┬────────┬──────┘
               │        │                    │        │
             YES       NO                   YES      NO
               │        │                    │        │
               ▼        │                    │        ▼
     ┌─────────────┐   │                    │   ┌──────────┐
     │ PDF format  │   │                    │   │  MUST use│
     │ standard?   │   │                    │   │  CONFIG  │
     └──────┬──┬───┘   │                    │   └──────────┘
            │  │       │                    │
          YES NO       │                    │
            │  │       │                    │
            ▼  ▼       ▼                    ▼
       ┌─────────┐ ┌──────────┐      ┌──────────┐
       │ CONFIG  │ │    AI    │      │    AI    │
       │ DRIVEN  │ │ POWERED  │      │ POWERED  │
       └─────────┘ └──────────┘      └──────────┘
            │           │                  │
            │           │                  │
            └───────────┴──────────────────┘
                        │
                        ▼
                ┌───────────────┐
                │ Excel Output  │
                └───────────────┘


SPECIFIC SCENARIOS
──────────────────

Scenario 1: Quarterly report from Britannia
  → Company: In config ✓
  → Format: Standard ✓
  → Decision: CONFIG-DRIVEN
  → Reason: Fastest, most accurate, free

Scenario 2: New startup's financial report
  → Company: Not in config ✗
  → Decision: AI-POWERED
  → Reason: Only option for unknown companies

Scenario 3: HUL report with unusual format
  → Company: In config ✓
  → Format: Non-standard ✗
  → Decision: AI-POWERED
  → Reason: Better handling of variations

Scenario 4: Batch processing 100 PDFs
  → Company: All in config ✓
  → Budget: $0.20 for AI vs Free for config
  → Decision: CONFIG-DRIVEN
  → Reason: Cost savings ($20 saved)

Scenario 5: One-off custom report
  → Company: Not in config ✗
  → Budget: $0.002 OK ✓
  → Decision: AI-POWERED
  → Reason: No config setup time needed
```

---

## File Flow Diagrams

### Directory Structure After Processing

```
project-root/
│
├─ uploads/                          ← Temporary PDF storage
│  └─ [temp-uuid].pdf                  (Deleted after processing)
│
├─ output/                           ← Parsed results
│  ├─ BRITANNIA_Doc1/
│  │  ├─ Doc1-table-1.html           ← Used by AI
│  │  ├─ Doc1-table-1.md             ← Fallback for AI
│  │  ├─ Doc1-table-1.csv            ← Reference
│  │  └─ Doc1-financial-data.json    ← Config-driven result
│  │
│  ├─ ITC_Doc2/
│  │  ├─ Doc2-table-1.html
│  │  ├─ Doc2-table-2.html           ← Multiple tables
│  │  ├─ Doc2-table-1.md
│  │  └─ Doc2-financial-data.json
│  │
│  └─ NEWCOMPANY_Doc3/
│     ├─ Doc3-table-1.html
│     ├─ Doc3-table-1.md
│     └─ Doc3-table-1.csv            ← No JSON (AI only)
│
└─ excel_storage/                    ← Generated Excel files
   ├─ metadata.json                    (File tracking)
   ├─ abc123-def456.xlsx               (UUID filenames)
   ├─ xyz789-ghi012.xlsx
   └─ mno345-pqr678.csv


FILE LIFECYCLE
──────────────

PDF → Upload
  │
  ├─ Saved to: uploads/[uuid].pdf
  │
  ▼ Parse
  │
  ├─ Created: output/{COMPANY}_{DOC}/
  │            ├─ .html (permanent)
  │            ├─ .md (permanent)
  │            └─ .csv (permanent)
  │
  ├─ Config-driven adds:
  │   └─ financial-data.json
  │
  ▼ Generate Excel
  │
  ├─ Saved to: excel_storage/[uuid].xlsx
  │  (with metadata.json entry)
  │
  └─ Download
     │
     └─ File persists until manual deletion
```

### Data Transformation Flow

```
PDF TABLE (Raw)
═══════════════════════════════════════════════════════════
| Particulars              | 30.06.25 | 31.03.25 | ...    |
|──────────────────────────|──────────|──────────|────────|
| Sale of goods            | 4,357.64 | 4,218.90 | ...    |
| Other operating revenue  |   123.45 |   145.67 | ...    |
| Revenue from operations  | 4,481.09 | 4,364.57 | ...    |
| Other income             |    56.78 |    67.89 | ...    |
| Total income             | 4,537.87 | 4,432.46 | ...    |
═══════════════════════════════════════════════════════════
                            │
                            ▼
HTML/MARKDOWN (Intermediate)
═══════════════════════════════════════════════════════════
<table>
  <tr>
    <td>Sale of goods</td>
    <td>4,357.64</td>
    <td>4,218.90</td>
  </tr>
  ...
</table>
═══════════════════════════════════════════════════════════
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
      CONFIG-DRIVEN                  AI-POWERED
      ═════════════                  ══════════
      BeautifulSoup                  OpenAI GPT
      + config.json                  + AI prompt
              │                           │
              └─────────────┬─────────────┘
                            ▼
JSON (Structured)
═══════════════════════════════════════════════════════════
{
  "company_name": "BRITANNIA",
  "financial_data": {
    "30.06.2025": {
      "sale_of_goods": 4357.64,
      "other_operating_revenues": 123.45,
      "revenue_from_operations": 4481.09,    ← Sum of above
      "other_income": 56.78,                 ← SEPARATE
      "total_income": 4537.87                ← ops + other
    },
    "31.03.2025": { ... }
  },
  "metadata": {
    "extraction_method": "tr_number" | "openai"
  }
}
═══════════════════════════════════════════════════════════
                            │
                            ▼
EXCEL (Final Output)
═══════════════════════════════════════════════════════════
Row | Particulars                    | B         | C     |...
────|────────────────────────────────|-----------|-------|---
1   | BRITANNIA                      |           |       |
2   | INR Crs                        | Unaud Q1  | FY 25 |
3   | I. Revenue from operations     | 3M-Jun 25 | 12M   |
4   |                                |           |       |
5   | Sale of goods                  | 4,357.64  |4,218.9|
6   | Other operating revenues       |   123.45  | 145.67|
7   | Total revenue from operations  | 4,481.09  |4,364.5|  ← Sum
8   | Other income                   |    56.78  |  67.89|  ← Separate
9   | Total Income (I+II)            | 4,537.87  |4,432.4|  ← ops+other
═══════════════════════════════════════════════════════════

KEY TRANSFORMATIONS:
• Numbers: "4,357.64" (string) → 4357.64 (float) → "4,357.64" (formatted)
• Negatives: "(123)" or "-123" → -123.0 → "(123)" in Excel
• Empty: "" or null → 0.0 → "-" in Excel
• Yearly: "31.03.2025_Y" → Column with "12M" label
```

---

## API Call Sequences

### Config-Driven Sequence

```
CLIENT                    FLASK API                  PARSER_CORE
  │                          │                            │
  │  POST /api/parse         │                            │
  ├─────────────────────────>│                            │
  │  File: PDF               │                            │
  │  company_name: BRITANNIA │                            │
  │                          │  process_pdf_document()    │
  │                          ├───────────────────────────>│
  │                          │                            │
  │                          │                        Page Detection
  │                          │                            │
  │                          │                        Docling Extract
  │                          │                            │
  │                          │                        Save HTML/MD/CSV
  │                          │                            │
  │                          │                        Parse with Config
  │                          │                            │
  │                          │<───────────────────────────┤
  │                          │  Return: financial_data    │
  │                          │                            │
  │<─────────────────────────┤                            │
  │  200 OK                  │                            │
  │  {                       │                            │
  │    "financial_data": {}  │                            │
  │    "output_files": {}    │                            │
  │  }                       │                            │
  │                          │                            │
  │  POST /api/generate-excel│                            │
  ├─────────────────────────>│                            │
  │  Body: financial_data    │                            │
  │                          │                            │
  │                          │  FinancialExcelGenerator   │
  │                          │  .generate_excel()         │
  │                          │                            │
  │<─────────────────────────┤                            │
  │  200 OK                  │                            │
  │  Content: Excel binary   │                            │
  │                          │                            │

TIMING:
  Parse:          12s
  Generate Excel: 2s
  ───────────────────
  Total:          14s
```

### AI-Powered Sequence

```
CLIENT              FLASK API           AI_EXTRACTOR         OPENAI
  │                    │                      │                 │
  │  POST /api/parse   │                      │                 │
  ├───────────────────>│                      │                 │
  │  (Same as config)  │                      │                 │
  │                    │                      │                 │
  │<───────────────────┤                      │                 │
  │  HTML/MD saved     │                      │                 │
  │                    │                      │                 │
  │  POST /api/        │                      │                 │
  │  generate-excel-ai │                      │                 │
  ├───────────────────>│                      │                 │
  │  {                 │                      │                 │
  │    company_name,   │                      │                 │
  │    document_name   │                      │                 │
  │  }                 │                      │                 │
  │                    │  extract_from_html() │                 │
  │                    ├─────────────────────>│                 │
  │                    │                      │  chat.create()  │
  │                    │                      ├────────────────>│
  │                    │                      │  System+User    │
  │                    │                      │  Prompt         │
  │                    │                      │                 │
  │                    │                      │  Processing...  │
  │                    │                      │  (2-5 seconds)  │
  │                    │                      │                 │
  │                    │                      │<────────────────┤
  │                    │                      │  JSON Response  │
  │                    │                      │  (3500 tokens)  │
  │                    │<─────────────────────┤                 │
  │                    │  financial_data dict │                 │
  │                    │                      │                 │
  │                    │  FinancialExcelGenerator              │
  │                    │  .generate_excel()   │                 │
  │                    │                      │                 │
  │<───────────────────┤                      │                 │
  │  200 OK            │                      │                 │
  │  Content: Excel    │                      │                 │
  │  Headers:          │                      │                 │
  │    X-Model: gpt..  │                      │                 │
  │    X-Tokens: 3500  │                      │                 │
  │                    │                      │                 │

TIMING:
  Parse:          12s
  AI Extract:     4s
  Generate Excel: 2s
  ───────────────────
  Total:          18s

COST:
  OpenAI API: $0.00226 (3500 tokens)
```

### Streamlit UI Workflow (AI Excel Generator Tab)

```
USER INTERACTION FLOW (v2.3 Update)
════════════════════════════════════

STEP 1: SELECT DOCUMENTS
─────────────────────────
┌─────────────────────────────────────┐
│  📋 Select Parsed Documents         │
│                                     │
│  ☐ BRITANNIA - Doc1                 │
│  ☑ ITC - Doc2                       │
│  ☑ P&G - Doc3                       │
│                                     │
│  ✅ Selected 2 document(s)           │
│  🏢 Multi-company: ITC, P&G          │
└─────────────────────────────────────┘
           │
           ▼

STEP 2: CONFIGURE OPTIONS
──────────────────────────
┌─────────────────────────────────────┐
│  ⚙️ Advanced Options                 │
│                                     │
│  ◉ Preferred Format: markdown       │
│  ○ Preferred Format: html           │
│                                     │
│  ☑ Save to File Storage             │  ← NEW v2.3 Feature
│     (Access from Saved Files tab)   │
└─────────────────────────────────────┘
           │
           ▼

STEP 3: UPLOAD TEMPLATE (Optional)
───────────────────────────────────
┌─────────────────────────────────────┐
│  📋 Custom Excel Template            │
│                                     │
│  [Choose File] template.xlsx        │
│  ✅ Template uploaded                │
│                                     │
│  Auto-detects:                      │
│  • Company names from Row 1         │
│  • Periods from Row 2 headers       │
│  • Metric names from Column A       │
└─────────────────────────────────────┘
           │
           ▼

STEP 4: GENERATE EXCEL
──────────────────────
┌─────────────────────────────────────┐
│  [🚀 Generate Excel with AI]         │
└──────────────────┬──────────────────┘
                   │
                   ▼
        ┌──────────────────┐
        │  Processing...   │
        │  🤖 AI extracting │
        │  from 2 docs     │
        └────────┬─────────┘
                 │
                 ▼

STEP 5A: SUCCESS (save_to_storage = FALSE)
───────────────────────────────────────────
┌─────────────────────────────────────────────┐
│  ✅ Excel file generated successfully!       │
│                                             │
│  📊 AI Model: gpt-4o-mini                   │
│  📊 Total Tokens: 5,200                     │
│  📊 Documents: 2                            │
│                                             │
│  [📥 Download Excel File]  ← Download button│
│                                             │
│  🎈 (Balloons animation)                    │
└─────────────────────────────────────────────┘


STEP 5B: SUCCESS (save_to_storage = TRUE)  ← NEW v2.3
─────────────────────────────────────────────────────
┌─────────────────────────────────────────────────┐
│  ✅ File has been saved to storage!              │
│                                                 │
│  📁 File ID: `abc123-def456`                    │
│  Download URL: /api/files/download/abc123...   │
│                                                 │
│  ℹ️ Go to the 'Saved Files' tab above to        │
│     view, manage, and download your file.      │
│                                                 │
│  🎈 (Balloons animation)                        │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│  📂 Navigate to "Saved Files" Tab               │
│                                                 │
│  Files List:                                    │
│  ┌───────────────────────────────────────────┐ │
│  │ 📊 financial_statement_consolidated.xlsx  │ │
│  │    Company: ITC, P&G                      │ │
│  │    Type: Consolidated (2 companies)       │ │
│  │    Date: 2026-01-06 14:30                 │ │
│  │    Size: 45 KB                            │ │
│  │    [📥 Download] [🗑️ Delete]               │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘


KEY DIFFERENCES (v2.3 Update)
─────────────────────────────

BEFORE (v2.2):
  save_to_storage = TRUE
    ↓
  Show download button + navigation hint
  ↓
  User could download OR navigate to Saved Files


AFTER (v2.3):
  save_to_storage = TRUE
    ↓
  NO download button (removed redundancy)
  ↓
  Clear navigation message only
  ↓
  User MUST navigate to Saved Files tab
  ↓
  Better organization & file management


RATIONALE:
──────────
• File already in storage → no need for immediate download
• Encourages using Saved Files tab for better tracking
• Reduces UI clutter (one less button)
• Consistent workflow: save → navigate → manage
• Download available in Saved Files with metadata
```

---

## Architecture Components

### System Component Diagram

```
┌───────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                          │
├──────────────────────────────┬────────────────────────────────────┤
│                              │                                    │
│     FLASK REST API           │      STREAMLIT WEB UI              │
│     (app.py)                 │      (streamlit_app.py)            │
│                              │                                    │
│  • 12+ endpoints             │  • 3-tab interface (v2.3)          │
│  • File upload               │    - Upload & Parse                │
│  • Parse/Generate            │    - AI Excel Generator            │
│  • CORS enabled              │    - Saved Files                   │
│                              │  • Multi-company consolidation     │
│                              │  • File management & tracking      │
│                              │                                    │
└──────────────┬───────────────┴────────────────┬───────────────────┘
               │                                │
               │         ┌──────────────────────┘
               │         │
               ▼         ▼
┌───────────────────────────────────────────────────────────────────┐
│                         BUSINESS LOGIC LAYER                      │
├────────────────────┬──────────────────┬───────────────────────────┤
│                    │                  │                           │
│  PARSER_CORE       │  AI_EXTRACTOR    │  EXCEL_GENERATOR          │
│  (parser_core.py)  │  (ai_extractor.py)│  (excel_generator.py)    │
│                    │                  │                           │
│  • Page detection  │  • OpenAI client │  • Excel formatting       │
│  • Table selection │  • Prompt engine │  • CSV generation         │
│  • Config parsing  │  • Validation    │  • File management        │
│  • Fuzzy matching  │  • JSON cleaning │  • Indian numbers         │
│                    │                  │                           │
└────────┬───────────┴────────┬─────────┴─────────┬─────────────────┘
         │                    │                   │
         ▼                    ▼                   ▼
┌───────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES LAYER                      │
├────────────────────┬──────────────────┬───────────────────────────┤
│                    │                  │                           │
│  DOCLING           │  OPENAI API      │  FILE SYSTEM              │
│                    │                  │                           │
│  • PDF parsing     │  • GPT-4o-mini   │  • uploads/               │
│  • OCR (EasyOCR)   │  • Chat API      │  • output/                │
│  • Table Former    │  • JSON mode     │  • excel_storage/         │
│  • Cell matching   │                  │                           │
│                    │                  │                           │
└────────────────────┴──────────────────┴───────────────────────────┘


DATA STRUCTURES
───────────────

1. CONFIG.JSON (Company Rules)
   {
     "britannia": {
       "column_layout": "standard",
       "financial_data": [
         {
           "key": "sale_of_goods",
           "labels": ["Sale of goods"],
           "tr_number": 5
         }
       ]
     }
   }

2. EXTRACTED JSON (Parsed Data)
   {
     "company_name": "BRITANNIA",
     "financial_data": {
       "30.06.2025": {
         "sale_of_goods": 4357.64,
         "revenue_from_operations": 4481.09,  ← Calculated
         "other_income": 56.78,               ← Separate
         "total_income": 4537.87              ← ops + other
       }
     }
   }

3. METADATA.JSON (File Tracking)
   {
     "files": {
       "abc123-def456": {
         "filename": "abc123-def456.xlsx",
         "company": "BRITANNIA",
         "file_type": "excel",
         "created_at": "2026-01-05T10:30:00",
         "download_count": 3
       }
     }
   }
```

### Revenue Calculation Logic

```
┌────────────────────────────────────────────────────────────────┐
│           REVENUE HIERARCHY (CRITICAL FOR AI PROMPT)           │
└────────────────────────────────────────────────────────────────┘

LEVEL 1: OPERATING REVENUE COMPONENTS
──────────────────────────────────────
┌─────────────────────────┐
│  Sale of goods          │  (key: sale_of_goods)
└────────┬────────────────┘
         │
┌────────┴────────────────┐
│  Export sales           │  (key: export_sales)
└────────┬────────────────┘
         │
┌────────┴────────────────┐
│  Service revenue        │  (key: service_revenue)
└────────┬────────────────┘
         │
┌────────┴────────────────┐
│  Other operating rev    │  (key: other_operating_revenues)
└────────┬────────────────┘
         │
         │ SUM (Operating only)
         ▼
┌──────────────────────────────────────┐
│  REVENUE FROM OPERATIONS             │  (key: revenue_from_operations)
│                                      │
│  = sale_of_goods                     │
│    + export_sales                    │
│    + service_revenue                 │
│    + other_operating_revenues        │
│                                      │
│  ⚠️ DOES NOT INCLUDE other_income    │
└────────┬─────────────────────────────┘


LEVEL 2: NON-OPERATING INCOME
──────────────────────────────
         │
         │ (Operating revenue above)
         │
┌────────┴────────────────┐
│  Other income           │  (key: other_income)
│                         │
│  Examples:              │
│  • Interest income      │
│  • Dividend income      │
│  • Gain on investments  │
│  • Foreign exchange gain│
│                         │
│  ⚠️ SEPARATE from ops   │
└────────┬────────────────┘
         │
         │ ADD (Operating + Non-operating)
         ▼
┌──────────────────────────────────────┐
│  TOTAL INCOME                        │  (key: total_income)
│                                      │
│  = revenue_from_operations           │
│    + other_income                    │
│                                      │
│  ✓ Complete income                   │
└──────────────────────────────────────┘


AI PROMPT INSTRUCTIONS (Critical Rules)
────────────────────────────────────────

✅ CORRECT:
revenue_from_operations = sale_of_goods + export_sales +
                         service_revenue + other_operating_revenues

total_income = revenue_from_operations + other_income


❌ INCORRECT (Common AI mistake):
revenue_from_operations = sale_of_goods + ... + other_income  ← WRONG!
  │
  └─ other_income is NON-OPERATING, must be SEPARATE


VALIDATION:
───────────
IF revenue_from_operations exists in table:
  → Use table value
ELSE:
  → Calculate from components (excluding other_income)

IF total_income exists in table:
  → Use table value
ELSE:
  → Calculate as: revenue_from_operations + other_income
```

---

## Error Handling Flows

### Config-Driven Error Flow

```
START: Parse PDF
  │
  ├─ Company not in config?
  │  └─> ERROR: "Unknown company. Supported: BRITANNIA, COLGATE..."
  │      → Suggest: Use AI-powered instead
  │
  ├─ No financial page found?
  │  └─> WARNING: "Processing entire document..."
  │      → Fallback: Parse all pages
  │
  ├─ No tables found?
  │  └─> ERROR: "No tables detected in PDF"
  │      → Check: PDF quality, OCR settings
  │
  ├─ Multiple tables, low confidence?
  │  └─> WARNING: "Selected table with score: 42"
  │      → Review: May not be correct table
  │
  ├─ tr_number fails, fuzzy succeeds?
  │  └─> INFO: "Using fuzzy matching (7/35 items)"
  │      → Normal: PDF format variation
  │
  └─ Both methods fail for item?
     └─> WARNING: "Could not extract: deferred_tax"
         → Result: Empty value in Excel
```

### AI-Powered Error Flow

```
START: AI Excel Generation
  │
  ├─ No HTML/MD files found?
  │  └─> ERROR: "Run /api/parse first"
  │      → Solution: Parse PDF before AI extraction
  │
  ├─ OPENAI_API_KEY missing?
  │  └─> ERROR: "OPENAI_API_KEY not set"
  │      → Solution: Add to .env file
  │
  ├─ OpenAI API error?
  │  ├─> Rate limit exceeded
  │  │   └─> ERROR: "Too many requests"
  │  │       → Retry: Wait 60 seconds
  │  │
  │  ├─> Invalid API key
  │  │   └─> ERROR: "Invalid authentication"
  │  │       → Check: API key in .env
  │  │
  │  └─> Network error
  │      └─> ERROR: "Connection timeout"
  │          → Check: Internet connection
  │
  ├─ Invalid JSON from AI?
  │  └─> ERROR: "Failed to parse JSON response"
  │      → Retry: With markdown format
  │
  ├─ Missing required fields?
  │  └─> ERROR: "Missing 'financial_data' key"
  │      → Log: Raw AI response for debugging
  │
  └─ Revenue calculation wrong?
     └─> WARNING: "Revenue != sum of components"
         → Fallback: Use table values, not calculated
```

---

## Performance Optimization

### Bottleneck Analysis

```
CONFIG-DRIVEN TIMELINE (Total: 12s)
═══════════════════════════════════════════════════════════

0s ────────────────────────────────────────────────── 12s
│                                                      │
├─ PDF Upload (0.5s)
│  └─ Network transfer
│
├─────── Page Detection (0.8s)
│        └─ PyPDF text extraction (fast)
│
├────────────────── Docling Extraction (8.2s) ──── BOTTLENECK
│                   │
│                   ├─ OCR processing (4.5s)
│                   ├─ Table structure (2.8s)
│                   └─ Cell matching (0.9s)
│
├─ Config Parsing (0.6s)
│  └─ HTML parsing + fuzzy matching
│
└─ File I/O (1.9s)
   └─ Save HTML, MD, CSV, JSON


AI-POWERED TIMELINE (Total: 18s)
═══════════════════════════════════════════════════════════

0s ────────────────────────────────────────────────── 18s
│                                                      │
├─────────────── Docling (same as above) ──────────────
│
├─ Load HTML (0.1s)
│
├──────── OpenAI API Call (4.2s) ────────── BOTTLENECK
│         │
│         ├─ Request transmission (0.2s)
│         ├─ AI processing (3.8s)
│         └─ Response parsing (0.2s)
│
├─ JSON validation (0.2s)
│
└─ Excel generation (1.9s)


OPTIMIZATION STRATEGIES
───────────────────────

1. Reduce Docling time:
   ✓ Process only target page (not entire PDF)
   ✓ Use CPU instead of GPU (better for single docs)
   ✗ Disable OCR (loses accuracy for scanned PDFs)

2. Reduce AI time:
   ✓ Truncate HTML to 30KB (saves tokens)
   ✓ Use gpt-4o-mini instead of gpt-4 (5x faster, 10x cheaper)
   ✗ Lower temperature (already at 0.1 minimum)

3. Cache results:
   ✓ Save intermediate files (HTML/MD) for re-processing
   ✓ Store generated Excel files with IDs
   ✗ Cache AI responses (violates OpenAI TOS)
```

---

## Best Practices Summary

### Development Guidelines

```
┌──────────────────────────────────────────────────────────────┐
│                      DO's and DON'Ts                         │
└──────────────────────────────────────────────────────────────┘

✅ DO:
─────
• Always run /api/parse before generate-excel-ai
• Set OPENAI_API_KEY in .env (never hardcode)
• Use HTML format for AI (better structure than MD)
• Validate JSON structure after AI extraction
• Track tokens_used for cost monitoring
• Save intermediate files (HTML/MD) for debugging
• Use config-driven when company is supported
• Apply Indian number formatting (commas, brackets)
• Follow revenue calculation hierarchy strictly


❌ DON'T:
──────────
• Include other_income in revenue_from_operations
• Skip validation after AI extraction
• Hardcode period mappings (use dynamic detection)
• Delete intermediate files (needed for re-generation)
• Use gpt-4 when gpt-4o-mini suffices (10x cost)
• Batch AI calls in parallel (rate limits)
• Trust AI output blindly (validate structure)
• Mix config keys (use exact names)


⚠️ COMMON PITFALLS:
───────────────────
1. Revenue Calculation Error
   Problem: AI adds other_income to revenue_from_operations
   Solution: Updated prompt with explicit hierarchy

2. File Not Found
   Problem: Trying AI extraction before parsing
   Solution: Always parse first to create HTML/MD

3. API Key Error
   Problem: OPENAI_API_KEY not set
   Solution: Create .env file with key

4. Rate Limiting
   Problem: Too many AI requests
   Solution: Add delays between batch processing
```

---

## Edge Cases & Limitations

### Currently Unsupported Scenarios

```
┌────────────────────────────────────────────────────────────────┐
│                    KNOWN LIMITATIONS                           |
└────────────────────────────────────────────────────────────────┘

❌ NOT SUPPORTED (Will Fail):
──────────────────────────────

1. Multiple Financial Tables Per Period
   ┌─────────────────────────────────────┐
   │ PDF has:                            |
   │ • Table 1: Standalone results       │
   │ • Table 2: Consolidated results     │
   │ • Table 3: Segment results          │
   └─────────────────────────────────────┘
   Issue: System picks ONE table (may be wrong)
   Workaround: Manual selection needed
   Status: ⚠️ Partial support via table scoring

2. Non-Standard Period Formats
   ❌ "Q1FY25" instead of "30.06.2025"
   ❌ "1st Quarter" instead of date
   ❌ "H1 2025" (half-yearly)
   ❌ "9M 2025" (9 months)

   Supported: ✓ DD.MM.YYYY format only
   AI: May extract but won't map to columns correctly

3. Multi-Currency Reports
   ┌─────────────────────────────────────┐
   │ Values in:                          |
   │ • INR Crores                        │
   │ • USD Millions                      │
   │ • EUR Millions                      │
   └─────────────────────────────────────┘
   Issue: No currency conversion/detection
   Result: Mixed units in same Excel

4. Non-INR Crores Unit
   ❌ INR Lakhs (need ×10 conversion)
   ❌ INR Thousands (need ×10,000 conversion)
   ❌ Actual values (need ×10,000,000 conversion)

   Supported: ✓ INR Crores only
   Impact: Wrong magnitude in Excel

5. Merged/Split Cells in Source PDF
   ┌─────────────────────────────────────┐
   │ Particulars      | Q1 | Q2 | Q1PY   │
   │ Revenue          | 100| 110| 90     │
   │   Sale of goods ─┴────┴────┴─────   │ ← Merged
   │   Services                          │
   └─────────────────────────────────────┘
   Issue: Cell matching fails
   AI: May misalign values to wrong periods

6. Vertical Table Layout (Transposed)
   ┌─────────────────────────────────────┐
   │ Particulars     | Revenue | Expense │
   │ 30.06.2025      | 4,357   | 2,100   │
   │ 31.03.2025      | 4,218   | 2,050   │
   └─────────────────────────────────────┘
   Issue: Expects horizontal layout
   Result: Complete extraction failure

7. Image-Based PDFs (Scanned Documents)
   ┌─────────────────────────────────────┐
   │ [IMAGE OF TABLE]                    │
   │ No selectable text                  │
   └─────────────────────────────────────┘
   Issue: OCR may fail for:
   • Poor scan quality
   • Handwritten annotations
   • Watermarks over text
   • Tilted/skewed scans

   Success Rate: 60-80% with good scans

8. Footnotes & References in Cells
   ┌─────────────────────────────────────┐
   │ Sale of goods¹   | 4,357.64         │
   │ ¹Includes exports                   │
   └─────────────────────────────────────┘
   Issue: Footnote symbols in keys
   Result: "sale_of_goods¹" ≠ "sale_of_goods"

9. Conditional Formatting/Colors
   • Red text for losses
   • Green for profits
   • Bold for totals

   Issue: Lost in extraction (HTML is plain)
   Impact: No visual emphasis in Excel

10. Multi-Page Tables (CRITICAL)
    ┌─────────────────────────────────────┐
    │ Page 3: Rows 1-20                   │
    │ Page 4: Rows 21-40 (continued)      │
    │ Page 5: Rows 41-50 (continued)      │
    └─────────────────────────────────────┘
    Issue: Treated as separate tables
    Result: Incomplete data extraction
    Impact: Missing metrics, wrong calculations
    Common in: Annual reports, detailed statements

11. Multi-Year Comparative Data (>11 Periods)
    ┌─────────────────────────────────────┐
    │ Financial statement with:           │
    │ • FY 2025 (12M)                     │
    │ • FY 2024 (12M)                     │
    │ • FY 2023 (12M)                     │
    │ • FY 2022 (12M)                     │
    │ • FY 2021 (12M)                     │
    │ = 5 periods                         │
    │                                     │
    │ OR Quarterly for 3 years:           │
    │ • 12 quarters = 12+ periods         │
    └─────────────────────────────────────┘
    Issue: Hardcoded PERIOD_MAPPING has only 11 columns
    Result: Extra periods are not mapped/displayed
    Impact: Data loss, incomplete Excel
    Workaround: Manual column addition needed

12. Consolidated Multi-Company Reports
    ┌───────────────────────────────────────┐
    │ Need: Single Excel with all companies │
    │                                       │
    │ Britannia Q2 2025                     │
    │ Colgate Q2 2025                       │
    │ Dabur Q2 2025                         │
    │ HUL Q2 2025                           │
    │ ... (all 7 companies)                 │
    │                                       │
    │ Combined in one Excel workbook        │
    │ with separate sheets or rows          │
    └───────────────────────────────────────┘
    Issue: No API endpoint for multi-company consolidation
    Current: Each company generates separate Excel
    Use Case: Portfolio analysis, comparative reports
    Workaround: Manual Excel merging required
    Status: Feature not implemented
```

### Testing Checklist

```
┌────────────────────────────────────────────────────────────────┐
│                  TESTING SCENARIOS                             │
└────────────────────────────────────────────────────────────────┘

✅ TESTED & WORKING:
────────────────────
• ✓ Britannia quarterly results (config)
• ✓ Colgate quarterly results (config)
• ✓ Dabur quarterly results (config)
• ✓ HUL quarterly results (config)
• ✓ ITC quarterly results (config)
• ✓ Nestlé quarterly results (config)
• ✓ P&G quarterly results (config)
• ✓ AI extraction on unknown company
• ✓ 4 periods extraction (Q1, Q4, Q1PY, FY)
• ✓ Negative values with brackets
• ✓ Indian number formatting
• ✓ Excel file generation
• ✓ CSV file generation
• ✓ File storage with UUIDs
• ✓ Metadata tracking
• ✓ Download counts
• ✓ Multiple table selection (heuristic)
• ✓ Fuzzy matching fallback
• ✓ Page detection (standalone priority)

⏳ NEEDS TESTING:
─────────────────
• ⏳ 8+ periods in same report
• ⏳ Half-yearly (H1/H2) results
• ⏳ Consolidated statements (edge cases)
• ⏳ Banks/NBFC reports
• ⏳ Insurance company reports
• ⏳ Segment-wise results
• ⏳ Foreign currency reports
• ⏳ PDFs with watermarks
• ⏳ Low-quality scanned PDFs
• ⏳ **Multi-page tables (table continuation)** ← CRITICAL
• ⏳ **Multi-year data (>11 periods)** ← CRITICAL
• ⏳ **Consolidated multi-company Excel** ← HIGH DEMAND
• ⏳ Batch processing (100+ PDFs)
• ⏳ Concurrent API requests
• ⏳ Rate limiting behavior
• ⏳ OpenAI API failures/retries
• ⏳ Very large PDFs (>50 pages)
• ⏳ Special characters in file names
• ⏳ International company formats
• ⏳ Restated/adjusted figures
• ⏳ Cost optimization (batch AI calls)
• ⏳ Excel with >11 periods (dynamic columns)

❌ KNOWN TO FAIL:
─────────────────
• ✗ Vertical table layouts (transposed)
• ✗ Non-INR currency units
• ✗ Non-crores units (lakhs, thousands)
• ✗ Image-only PDFs (no text layer)
• ✗ Password-protected PDFs
• ✗ Non-English PDFs
• ✗ Non-standard date formats
• ✗ Multi-currency in same table
• ✗ Embedded Excel tables in PDF
• ✗ Heavy merged cells
• ✗ **Multi-page table continuation** ← CONFIRMED
• ✗ **>11 periods (hardcoded limit)** ← CONFIRMED
• ✗ **Multi-company consolidation** ← NOT IMPLEMENTED
```

### Performance Benchmarks

```
┌────────────────────────────────────────────────────────────────┐
│              PERFORMANCE THRESHOLDS                            │
└────────────────────────────────────────────────────────────────┘

ACCEPTABLE PERFORMANCE:
───────────────────────
Config-Driven:
  • Small PDF (5 pages):     3-5 seconds   ✓
  • Medium PDF (15 pages):   8-12 seconds  ✓
  • Large PDF (50 pages):    20-30 seconds ✓

AI-Powered:
  • Small PDF (5 pages):     8-12 seconds  ✓
  • Medium PDF (15 pages):   12-18 seconds ✓
  • Large PDF (50 pages):    25-35 seconds ✓

DEGRADED PERFORMANCE (Investigate):
────────────────────────────────────
  • Config-Driven: >30 seconds
    → Check: Page count, OCR complexity, table count

  • AI-Powered: >40 seconds
    → Check: HTML size, OpenAI API latency, token count

UNACCEPTABLE PERFORMANCE (Optimization Needed):
────────────────────────────────────────────────
  • >60 seconds for any PDF
  • >10 seconds for OpenAI call alone
  • >50MB memory usage
  • >100MB disk usage per document

COST THRESHOLDS:
────────────────
AI Extraction:
  • Target: $0.001-$0.003 per document    ✓
  • Acceptable: <$0.005 per document      ⚠️
  • Expensive: >$0.01 per document        ✗

  If >$0.005:
    → Truncate HTML more aggressively
    → Use markdown instead of HTML
    → Switch to cheaper model (if available)

SCALABILITY LIMITS:
───────────────────
  • Concurrent API requests: 5 (Flask default)
  • Max file uploads/minute: 30 (no rate limit)
  • AI requests/minute: 10-15 (OpenAI tier 1)
  • Storage capacity: 10GB (no cleanup implemented)

  For production:
    → Add rate limiting middleware
    → Implement automatic cleanup (>30 days)
    → Use production WSGI server (Gunicorn)
    → Add Redis caching for parsed results
```

### Future Enhancements Needed

```
┌────────────────────────────────────────────────────────────────┐
│           IMPROVEMENTS TO ADDRESS EDGE CASES                   │
└────────────────────────────────────────────────────────────────┘

HIGH PRIORITY:
──────────────
1. Dynamic Period Detection (CRITICAL)
   Issue: Hardcoded 11 columns (PERIOD_MAPPING)
   Solution: Auto-detect period count, generate dynamic columns
   Impact: Support 15+ periods, half-yearly, 9M, multi-year formats
   Benefit: Handle annual reports with 5+ years of data
   Implementation: Refactor PERIOD_MAPPING to be data-driven

2. Multi-Page Table Stitching (CRITICAL)
   Issue: Tables split across pages treated as separate
   Solution:
     • Detect "continued" markers in headers/footers
     • Merge tables with matching column structure
     • Track page numbers for validation
   Impact: Handle complex annual reports correctly
   Benefit: Complete data extraction (no missing rows)
   Implementation: Add pre-processing step in Docling output

3. Multi-Company Consolidated Excel (HIGH DEMAND)
   Issue: No support for portfolio/comparative analysis
   Solution: New API endpoint `/api/generate-consolidated-excel`
   Options:
     A. Multiple sheets (one per company)
     B. Merged rows (sequential stacking)
     C. Pivot format (companies as columns)
   Impact: Enable portfolio managers, analysts, auditors
   Benefit: Single Excel for entire portfolio
   Implementation: New endpoint + batch processing logic

4. Unit Conversion Support
   Issue: Only INR Crores
   Solution: Detect unit, convert to standard
   Impact: Handle lakhs, thousands, actuals

5. Table Selection UI
   Issue: Automatic selection may be wrong
   Solution: Show all tables, let user choose
   Impact: Better accuracy for complex PDFs

6. Fuzzy Matching Threshold Config
   Issue: Fixed 80% threshold
   Solution: Per-company configurable threshold
   Impact: Reduce false positives

7. Company Name Normalization
   Issue: Case-sensitive matching
   Solution: Auto-convert to uppercase in API
   Impact: Better UX, fewer errors

MEDIUM PRIORITY:
────────────────
8. Period Format Flexibility
   Issue: Only DD.MM.YYYY supported
   Solution: Support Q1FY25, H1 2025, FY2024-25 formats
   Impact: Work with various reporting standards
   Benefit: International company support

9. OCR Post-Processing
   Issue: Treats as separate tables
   Solution: Detect "continued" markers, merge
   Impact: Handle complex annual reports

7. OCR Post-Processing
   Issue: Character misreading (0 vs O)
   Solution: Validation rules + corrections
   Impact: Better scanned PDF support

8. Caching Layer
   Issue: Re-parsing same PDF wastes time
   Solution: Redis cache for parsed results
   Impact: Faster repeat requests

9. Batch API Endpoint
   Issue: One PDF at a time
   Solution: /api/batch-parse for multiple PDFs
   Impact: Faster bulk processing

10. Error Recovery & Retries
    Issue: Single failure aborts
    Solution: Automatic retry with exponential backoff
    Impact: Handle transient OpenAI errors

LOW PRIORITY:
─────────────
11. Currency Detection & Conversion
    Issue: No multi-currency support
    Solution: Detect currency, apply exchange rates
    Impact: International company support

12. Custom Excel Templates
    Issue: Fixed 47-row format
    Solution: User-uploadable templates
    Impact: Different industry formats

13. Audit Trail
    Issue: No history of edits
    Solution: Track all JSON modifications
    Impact: Compliance, debugging

14. Webhook Notifications
    Issue: Synchronous processing only
    Solution: Async processing + webhooks
    Impact: Better UX for large PDFs

15. Advanced AI Models
    Issue: GPT-4o-mini sometimes inaccurate
    Solution: Fallback to GPT-4 for failures
    Impact: Better accuracy (higher cost)
```

---

## Quick Reference

### Command Cheatsheet

```
CONFIG-DRIVEN EXTRACTION
────────────────────────

# Step 1: Parse PDF
curl -X POST http://localhost:5000/api/parse \
  -F "file=@report.pdf" \
  -F "company_name=BRITANNIA" \
  > result.json

# Step 2: Generate Excel
curl -X POST http://localhost:5000/api/generate-excel \
  -H "Content-Type: application/json" \
  -d @result.json \
  --output statement.xlsx


AI-POWERED EXTRACTION
─────────────────────

# Step 1: Parse PDF (saves HTML)
curl -X POST http://localhost:5000/api/parse \
  -F "file=@report.pdf" \
  -F "company_name=NEWCO"

# Step 2: AI Extract + Generate Excel
curl -X POST http://localhost:5000/api/generate-excel-ai \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "NEWCO",
    "document_name": "NEWCO_report"
  }' \
  --output statement.xlsx


CHECKING RESULTS
────────────────

# List generated files
curl http://localhost:5000/api/list-generated-files

# Download by ID
curl http://localhost:5000/api/download-generated/abc123 \
  --output file.xlsx

# Check API health
curl http://localhost:5000/health
```

### File Patterns

```
INPUT PDF:           {Company}_Unaudited_Q2_June_2026.pdf
                     └─ Any name.pdf

OUTPUT DIRECTORY:    output/{COMPANY}_{DOCUMENT}/
                     └─ BRITANNIA_Britannia_Q2_June_2026/

HTML FILE:           {document}-table-1.html
                     └─ Britannia_Q2_June_2026-table-1.html

MARKDOWN FILE:       {document}-table-1.md

JSON FILE:           {document}-financial-data.json
                     └─ Only created by config-driven

EXCEL FILE:          {uuid}.xlsx
                     └─ Stored in excel_storage/

METADATA:            excel_storage/metadata.json
                     └─ Tracks all generated files
```

---

**Last Updated**: January 5, 2026  
**Version**: 2.2  
**Authors**: Financial Converter Team
