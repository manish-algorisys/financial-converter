"""
Check period mismatch between JSON and Excel PERIOD_MAPPING
"""
import json
from pathlib import Path

# Load JSON
json_path = Path("output/BRITANNIA_Britannia_Unaudited_Q2_June_2026/Britannia_Unaudited_Q2_June_2026-financial-data.json")
with open(json_path, 'r') as f:
    data = json.load(f)

# Periods in JSON
json_periods = set()
for item in data['financial_data']:
    json_periods.update(item['values'].keys())

# PERIOD_MAPPING from excel_generator.py
PERIOD_MAPPING = {
    '30.06.2025': ('B', 1, 'Unaudited Q1', '3M-30th Jun 2025'),
    '31.03.2025_Y': ('C', 2, 'FY 2025', '12M'),
    '31.03.2025': ('D', 3, 'Q4', '3M-31st Mar 2025'),
    '31.12.2024': ('E', 4, 'Q3', '3M-31st Dec 2024'),
    '30.09.2024': ('F', 5, 'Q2', '3M-30th Sept 2024'),
    '30.06.2024': ('G', 6, 'Unaudited Q1 FY 2024', '3M-30th Jun 2024'),
    '31.03.2024_Y': ('H', 7, 'FY 2024', '12M'),
    '31.03.2024': ('I', 8, 'Q4 FY 2024', '3M-31st Mar 2024'),
    '31.12.2023': ('J', 9, 'Q3 FY 2024', '3M-31st Dec 2023'),
    '30.09.2023': ('K', 10, 'Q2 FY 2024', '3M-30th Sept 2023'),
    '30.06.2023': ('L', 11, 'Q1 FY 2024', '3M-30th Jun 2023'),
}

excel_periods = set(PERIOD_MAPPING.keys())

print("="*80)
print("PERIOD MISMATCH ANALYSIS")
print("="*80)

print(f"\nPeriods in JSON: {len(json_periods)}")
for p in sorted(json_periods):
    print(f"  ✓ {p}")

print(f"\nPeriods in Excel PERIOD_MAPPING: {len(excel_periods)}")
for p in sorted(excel_periods):
    status = "✓" if p in json_periods else "✗"
    print(f"  {status} {p}")

matching = json_periods & excel_periods
print(f"\n{'='*80}")
print(f"MATCHING periods: {len(matching)}")
for p in sorted(matching):
    print(f"  ✓ {p}")

in_json_not_excel = json_periods - excel_periods
if in_json_not_excel:
    print(f"\n{'='*80}")
    print(f"⚠️  In JSON but NOT in Excel PERIOD_MAPPING: {len(in_json_not_excel)}")
    for p in sorted(in_json_not_excel):
        print(f"  ❌ {p} - THIS DATA WILL BE MISSING IN EXCEL!")

in_excel_not_json = excel_periods - json_periods
if in_excel_not_json:
    print(f"\n{'='*80}")
    print(f"In Excel PERIOD_MAPPING but NOT in JSON: {len(in_excel_not_json)}")
    for p in sorted(in_excel_not_json):
        print(f"  ○ {p} - Empty column in Excel")

print(f"\n{'='*80}")
print("CONCLUSION:")
print("-"*80)
if len(matching) == len(json_periods):
    print("✅ All JSON periods are mapped - Excel will show all data")
else:
    coverage = len(matching) / len(json_periods) * 100
    print(f"❌ Only {len(matching)}/{len(json_periods)} JSON periods are mapped ({coverage:.1f}%)")
    print(f"   {len(in_json_not_excel)} periods with data will be MISSING from Excel!")
    print(f"   Solution: Use dynamic period detection or update PERIOD_MAPPING")

print("="*80)
