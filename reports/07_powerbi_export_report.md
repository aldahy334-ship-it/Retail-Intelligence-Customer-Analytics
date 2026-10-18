# Step 8a - Power BI export

## Sanity checks
| Check | Computed | Expected | Status |
|---|---|---|---|
| fact_invoices rows | 53,628.00 | 53,628.00 | OK |
| Gross product sales | 19,700,954.46 | 19,700,954.46 | OK |
| Returns | -719,692.94 | -719,692.94 | OK |
| Net product revenue | 18,981,261.52 | 18,981,261.52 | OK |
| Orders | 39,516.00 | 39,516.00 | OK |
| Gross excluding D13 | 19,455,301.26 | 19,455,301.26 | OK |
| Returns excluding D13 | -474,039.74 | -474,039.74 | OK |
| D13 invoices flagged | 4.00 | 4.00 | OK |
| dim_calendar rows | 739.00 | 739.00 | OK |
| dim_customer rows (customers with orders) | 5,852.00 | 5,852.00 | OK |
| dim_customer net revenue (customers with orders) | 16,413,300.86 | 16,413,300.88 | OK |
| Segments: customers per segment vs 04_segment_summary.csv (sum of abs diff) | 0.00 | 0.00 | OK |
| dim_product rows | 4,739.00 | 4,739.00 | OK |
| dim_product gross sales | 19,700,954.46 | 19,700,954.46 | OK |
| dim_product returns | -719,692.94 | -719,692.94 | OK |
| Cohorts exported | 24.00 | 24.00 | OK |
| Base cohort (2009-12) customers | 951.00 | 951.00 | OK |
| Cohort month 0 = 100% | 100.00 | 100.00 | OK |

## Files written (folder: powerbi/)
| file | rows | columns |
|---|---|---|
| fact_invoices.csv | 53628 | invoice, invoice_date, invoice_month, customer_id, country, n_lines, units_sold, gross_sales, returns_amount, net_product_amount, shipping_amount, fee_adjustment_amount, is_order, is_cancel_invoice, is_d13, has_customer |
| dim_calendar.csv | 739 | date, year, month, month_name, year_month, quarter, weekday_num, weekday_name, is_partial_month, month_start |
| dim_country.csv | 43 | country, market, is_generic_label |
| dim_customer.csv | 5852 | customer_id, country, orders, first_order_date, last_order_date, recency_days, gross_sales, returns_amount, net_revenue, n_cancel_invoices, R, F, M, rfm_code, segment, segment_sort |
| dim_product.csv | 4739 | stock_code, product_description, units_sold, gross_sales, returns_amount, net_product_amount, units_returned, n_orders, n_customers, avg_unit_price, first_sale_date, last_sale_date, is_dotcom_code, is_d13_code, is_family_79323, return_rate_pct, product_rank, share_pct, cum_share_pct |
| fact_cohort_retention.csv | 300 | cohort, cohort_month, is_base, customers, months_since_first, active_pct, active_customers |

## Referential integrity (information)
- Invoices without Customer ID (blank customer_id): 8,752
- Customer IDs in fact_invoices but not in dim_customer (cancel-only customers and IDs outside customers.csv): 90
- Countries in fact_invoices but not in dim_country: 0

## Suggested relationships in the Power BI model
| from | to | type |
|---|---|---|
| fact_invoices[invoice_date] | dim_calendar[date] | many-to-one |
| fact_invoices[country] | dim_country[country] | many-to-one |
| fact_invoices[customer_id] | dim_customer[customer_id] | many-to-one (blank for anonymous orders) |
| fact_cohort_retention | no relationship (stand-alone table for the cohort page) | - |
| dim_product | no relationship (aggregated over the whole period, no date) | - |
