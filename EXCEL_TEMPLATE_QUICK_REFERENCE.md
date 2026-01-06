# Excel Template Quick Reference

## Placeholder Syntax

```
{{key[period]}}
```

## Common Placeholders

### Company Info

```
{{company_name}}
```

### Revenue (Q1 FY2026)

```
{{sale_of_goods[30.06.2025]}}
{{revenue_from_operations[30.06.2025]}}
{{other_income[30.06.2025]}}
{{total_income[30.06.2025]}}
```

### Expenses

```
{{cost_of_materials_consumed[30.06.2025]}}
{{employee_benefits_expense[30.06.2025]}}
{{total_expenses[30.06.2025]}}
```

### Profit

```
{{profit_before_tax[30.06.2025]}}
{{total_tax_expense[30.06.2025]}}
{{net_profit[30.06.2025]}}
```

### EPS

```
{{eps_basic[30.06.2025]}}
{{eps_diluted[30.06.2025]}}
```

## Period Reference

| Period    | Format         | Description           |
| --------- | -------------- | --------------------- |
| Q1 FY2026 | `30.06.2025`   | June 30, 2025         |
| Q2 FY2025 | `30.09.2024`   | September 30, 2024    |
| Q3 FY2025 | `31.12.2024`   | December 31, 2024     |
| Q4 FY2025 | `31.03.2025`   | March 31, 2025        |
| FY 2025   | `31.03.2025_Y` | Full year (note `_Y`) |
| FY 2024   | `31.03.2024_Y` | Full year             |

## Quick Example

```excel
A1: {{company_name}} Financial Summary
A2:
A3: Metric           | Q1 FY2026              | Q1 FY2025              | FY2025
A4: Revenue          | {{revenue_from_operations[30.06.2025]}} | {{revenue_from_operations[30.06.2024]}} | {{revenue_from_operations[31.03.2025_Y]}}
A5: Net Profit       | {{net_profit[30.06.2025]}} | {{net_profit[30.06.2024]}} | {{net_profit[31.03.2025_Y]}}
A6: EPS              | {{eps_basic[30.06.2025]}} | {{eps_basic[30.06.2024]}} | {{eps_basic[31.03.2025_Y]}}
```

## All Available Keys

- sale_of_goods
- export_sales
- service_revenue
- other_operating_revenues
- revenue_from_operations
- other_income
- total_income
- cost_of_materials_consumed
- excise_duty
- purchases_stock_in_trade
- changes_in_inventories
- employee_benefits_expense
- finance_costs
- depreciation_amortisation_expense
- other_expense
- advertising_expense
- impairment_losses
- total_expenses
- profit_before_exceptional_and_tax
- exceptional_item_expense
- profit_before_tax
- current_tax
- deferred_tax
- total_tax_expense
- net_profit
- oci_non_reclass_items
- tax_on_non_reclass_items
- other_comprehensive_income
- total_comprehensive_income
- paid_up_equity_share_capital
- other_equity
- eps_basic
- eps_diluted
