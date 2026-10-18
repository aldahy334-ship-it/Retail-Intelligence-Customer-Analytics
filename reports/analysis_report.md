# Analysis Profile Report
- المجلد: `.`

## 1. الجداول: الحجم والأعمدة وعيّنة
| Table | Rows | Expected (log) | Status |
|---|---|---|---|
| sales_lines | 1,033,062 | 1,033,062 | OK |
| non_sales_lines | 11,786 | 11,786 | OK |
| invoices | 53,628 | 53,628 | OK |
| customers | 5,875 | 5,875 | OK |
| products | 4,739 | 4,739 | OK |
| calendar | 739 | 739 | OK |

### sales_lines
| column | dtype | nulls |
|---|---|---|
| invoice | str | 0 |
| stock_code | str | 0 |
| description | str | 0 |
| quantity | int64 | 0 |
| price | float64 | 0 |
| line_amount | float64 | 0 |
| row_type | str | 0 |
| invoice_ts | str | 0 |
| invoice_day | str | 0 |
| customer_id | float64 | 227214 |
| country | str | 0 |
| is_exact_duplicate | bool | 0 |
| is_qty_outlier | bool | 0 |
| is_amount_outlier | bool | 0 |
| is_dotcom_code | bool | 0 |
| src_sheet | str | 0 |
| src_row | int64 | 0 |

أول 3 صفوف:
| invoice | stock_code | description | quantity | price | line_amount | row_type | invoice_ts | invoice_day | customer_id | country | is_exact_duplicate | is_qty_outlier | is_amount_outlier | is_dotcom_code | src_sheet | src_row |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 489434 | 85048 | 15CM CHRISTMAS GLASS BALL 20 LIGHTS | 12 | 6.95 | 83.4 | sale | 2009-12-01 07:45:00 | 2009-12-01 | 13085.0 | United Kingdom | False | False | False | False | Year 2009-2010 | 2 |
| 489434 | 79323P | PINK CHERRY LIGHTS | 12 | 6.75 | 81.0 | sale | 2009-12-01 07:45:00 | 2009-12-01 | 13085.0 | United Kingdom | False | False | False | False | Year 2009-2010 | 3 |
| 489434 | 79323W | WHITE CHERRY LIGHTS | 12 | 6.75 | 81.0 | sale | 2009-12-01 07:45:00 | 2009-12-01 | 13085.0 | United Kingdom | False | False | False | False | Year 2009-2010 | 4 |

### non_sales_lines
| column | dtype | nulls |
|---|---|---|
| invoice | str | 0 |
| stock_code | str | 0 |
| description | str | 4275 |
| quantity | int64 | 0 |
| price | float64 | 0 |
| line_amount | float64 | 0 |
| row_type | str | 0 |
| invoice_ts | str | 0 |
| invoice_day | str | 0 |
| customer_id | float64 | 8073 |
| country | str | 0 |
| is_exact_duplicate | bool | 0 |
| is_qty_outlier | bool | 0 |
| is_amount_outlier | bool | 0 |
| is_dotcom_code | bool | 0 |
| src_sheet | str | 0 |
| src_row | int64 | 0 |

أول 3 صفوف:
| invoice | stock_code | description | quantity | price | line_amount | row_type | invoice_ts | invoice_day | customer_id | country | is_exact_duplicate | is_qty_outlier | is_amount_outlier | is_dotcom_code | src_sheet | src_row |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 489439 | POST | POSTAGE | 3 | 18.0 | 54.0 | shipping | 2009-12-01 09:28:00 | 2009-12-01 | 12682.0 | France | False | False | False | False | Year 2009-2010 | 91 |
| 489444 | POST | POSTAGE | 1 | 141.0 | 141.0 | shipping | 2009-12-01 09:55:00 | 2009-12-01 | 12636.0 | United States | False | False | False | False | Year 2009-2010 | 128 |
| 489447 | POST | POSTAGE | 1 | 130.0 | 130.0 | shipping | 2009-12-01 10:10:00 | 2009-12-01 | 12362.0 | Belgium | False | False | False | False | Year 2009-2010 | 175 |

### invoices
| column | dtype | nulls |
|---|---|---|
| invoice | str | 0 |
| invoice_ts | str | 0 |
| customer_id | float64 | 8752 |
| country | str | 0 |
| n_lines | int64 | 0 |
| n_exact_dup_lines | int64 | 0 |
| n_line_timestamps | int64 | 0 |
| invoice_type | str | 0 |
| n_sale_lines | int64 | 0 |
| n_cancel_lines | int64 | 0 |
| units_sold | int64 | 0 |
| gross_sales | float64 | 0 |
| returns_amount | float64 | 0 |
| net_product_amount | float64 | 0 |
| shipping_amount | float64 | 0 |
| fee_adjustment_amount | float64 | 0 |
| has_customer | bool | 0 |
| is_uk | bool | 0 |

أول 3 صفوف:
| invoice | invoice_ts | customer_id | country | n_lines | n_exact_dup_lines | n_line_timestamps | invoice_type | n_sale_lines | n_cancel_lines | units_sold | gross_sales | returns_amount | net_product_amount | shipping_amount | fee_adjustment_amount | has_customer | is_uk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 489434 | 2009-12-01 07:45:00 | 13085.0 | United Kingdom | 8 | 0 | 1 | sale | 8 | 0 | 166 | 505.3 | 0.0 | 505.3 | 0.0 | 0.0 | True | True |
| 489435 | 2009-12-01 07:46:00 | 13085.0 | United Kingdom | 4 | 0 | 1 | sale | 4 | 0 | 60 | 145.79999999999998 | 0.0 | 145.79999999999998 | 0.0 | 0.0 | True | True |
| 489436 | 2009-12-01 09:06:00 | 13078.0 | United Kingdom | 19 | 0 | 1 | sale | 19 | 0 | 193 | 630.33 | 0.0 | 630.33 | 0.0 | 0.0 | True | True |

### customers
| column | dtype | nulls |
|---|---|---|
| customer_id | int64 | 0 |
| first_invoice_ts | str | 0 |
| last_invoice_ts | str | 0 |
| n_countries | int64 | 0 |
| country | str | 0 |
| units_sold | int64 | 0 |
| gross_sales | float64 | 0 |
| returns_amount | float64 | 0 |
| net_product_amount | float64 | 0 |
| n_orders | int64 | 0 |
| n_cancel_invoices | int64 | 0 |
| has_orders | bool | 0 |
| multi_country | bool | 0 |

أول 3 صفوف:
| customer_id | first_invoice_ts | last_invoice_ts | n_countries | country | units_sold | gross_sales | returns_amount | net_product_amount | n_orders | n_cancel_invoices | has_orders | multi_country |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 12346 | 2010-03-02 13:08:00 | 2011-01-18 10:17:00 | 1 | United Kingdom | 74239 | 77352.96 | -77183.6 | 169.36000000000058 | 3 | 1 | True | False |
| 12347 | 2010-10-31 14:20:00 | 2011-12-07 15:52:00 | 1 | Iceland | 2967 | 4921.53 | 0.0 | 4921.53 | 8 | 0 | True | False |
| 12348 | 2010-09-27 14:59:00 | 2011-09-25 13:13:00 | 1 | Finland | 2704 | 1658.4 | 0.0 | 1658.4 | 5 | 0 | True | False |

### products
| column | dtype | nulls |
|---|---|---|
| stock_code | str | 0 |
| units_sold | float64 | 0 |
| gross_sales | float64 | 0 |
| n_orders | float64 | 0 |
| n_customers | float64 | 0 |
| first_sale_ts | str | 14 |
| last_sale_ts | str | 14 |
| min_unit_price | float64 | 14 |
| max_unit_price | float64 | 14 |
| units_returned | float64 | 0 |
| returns_amount | float64 | 0 |
| avg_unit_price | float64 | 14 |
| product_description | str | 0 |
| n_descriptions_seen | int64 | 0 |
| is_dotcom_code | bool | 0 |
| net_product_amount | float64 | 0 |

أول 3 صفوف:
| stock_code | units_sold | gross_sales | n_orders | n_customers | first_sale_ts | last_sale_ts | min_unit_price | max_unit_price | units_returned | returns_amount | avg_unit_price | product_description | n_descriptions_seen | is_dotcom_code | net_product_amount |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10002 | 8676.0 | 6946.51 | 362.0 | 164.0 | 2009-12-01 09:08:00 | 2011-04-18 12:56:00 | 0.72 | 1.7 | 1223.0 | -883.5500000000001 | 0.8006581373905025 | INFLATABLE POLITICAL GLOBE | 1 | False | 6062.96 |
| 10002R | 4.0 | 20.57 | 3.0 | 0.0 | 2009-12-02 14:43:00 | 2010-01-25 17:36:00 | 5.06 | 5.17 | 0.0 | 0.0 | 5.1425 | ROBOT PENCIL SHARPNER | 1 | False | 20.57 |
| 10080 | 315.0 | 129.29 | 27.0 | 23.0 | 2009-12-02 16:02:00 | 2011-11-21 17:04:00 | 0.39 | 0.85 | 0.0 | 0.0 | 0.4104444444444444 | GROOVY CACTUS INFLATABLE | 1 | False | 129.29 |

### calendar
| column | dtype | nulls |
|---|---|---|
| date | str | 0 |
| year | int64 | 0 |
| month | int64 | 0 |
| month_name | str | 0 |
| year_month | str | 0 |
| quarter | int64 | 0 |
| weekday_num | int64 | 0 |
| weekday_name | str | 0 |
| is_partial_month | bool | 0 |

أول 3 صفوف:
| date | year | month | month_name | year_month | quarter | weekday_num | weekday_name | is_partial_month |
|---|---|---|---|---|---|---|---|---|
| 2009-12-01 | 2009 | 12 | December | 2009-12 | 4 | 2 | Tuesday | False |
| 2009-12-02 | 2009 | 12 | December | 2009-12 | 4 | 3 | Wednesday | False |
| 2009-12-03 | 2009 | 12 | December | 2009-12 | 4 | 4 | Thursday | False |

## 2. الأعمدة المكتشفة (تحقق أنها صحيحة)
| role | column in sales_lines |
|---|---|
| inv | invoice |
| qty | quantity |
| price | price |
| cust | customer_id |
| type | row_type |
| date | nan |
| stock | stock_code |
| country | country |
| dup | is_exact_duplicate |

## 3. توزيع row_type مقابل السجل
| row_type | Rows | Expected (log) | Status |
|---|---|---|---|
| sale | 1,015,088 | 1,015,088 | OK |
| cancellation | 17,974 | 17,974 | OK |
| stock_adjustment | 5,913 | 5,913 | OK |
| shipping | 3,788 | 3,788 | OK |
| fee_or_adjustment | 1,906 | 1,906 | OK |
| other_non_product | 118 | 118 | OK |
| zero_price_item | 61 | 61 | OK |
| unclassified | 0 | 0 | OK |

## 4. المقاييس الأساسية مقابل جدول D2
### مع الصفوف المكررة (النسخة الأساسية)
| Metric | Computed | Expected (log D2) | Status |
|---|---|---|---|
| Sale lines | 1,015,088 | 1,015,088 | OK |
| Orders | 39,516 | 39,516 | OK |
| Customers | 5,852 | 5,852 | OK |
| Units sold | 11,221,957 | 11,221,957 | OK |
| Gross product sales | 19,700,954.46 | 19,700,954.46 | OK |
| Returns | -719,692.94 | -719,692.94 | OK |
| Net product revenue | 18,981,261.52 | 18,981,261.52 | OK |
| AOV (mean) | 498.56 | 498.56 | OK |
| AOV (median) | 301.80 | - | - |

### بدون الصفوف المكررة (is_exact_duplicate)
| Metric | Computed | Expected (log D2) | Status |
|---|---|---|---|
| Sale lines | 1,003,357 | 1,003,357 | OK |
| Orders | 39,516 | 39,516 | OK |
| Customers | 5,852 | 5,852 | OK |
| Units sold | 11,188,061 | 11,188,061 | OK |
| Gross product sales | 19,643,861.64 | 19,643,861.64 | OK |
| Returns | -716,462.57 | -716,462.57 | OK |
| Net product revenue | 18,927,399.07 | 18,927,399.07 | OK |
| AOV (mean) | 497.11 | 497.11 | OK |
| AOV (median) | 301.23 | - | - |

## 5. Revenue Bridge
| Item | Amount |
|---|---|
| Gross product sales | 19,700,954.46 |
| Returns | -719,692.94 |
| Net product revenue | 18,981,261.52 |
| Shipping | 433,410.51 |
| Fees & adjustments (+ other_non_product) | -504,909.91 |
| TOTAL | 18,909,762.12 |

## 6. التحقق من الطلبين الضخمين (D13)
| inv | stock | qty | price | amt | type | cust | date |
|---|---|---|---|---|---|---|---|
| 541431 | 23166 | 74215 | 1.04 | 77183.6 | sale | 12346.0 | NaT |
| C541433 | 23166 | -74215 | 1.04 | -77183.6 | cancellation | 12346.0 | NaT |
| 581483 | 23843 | 80995 | 2.08 | 168469.6 | sale | 16446.0 | NaT |
| C581484 | 23843 | -80995 | 2.08 | -168469.6 | cancellation | 16446.0 | NaT |

| Item | Value |
|---|---|
| مبيعات الطلبين (sale) | 245,653.20 |
| إلغاء الطلبين (cancellation) | -245,653.20 |
| صافي الطلبين + إلغائهما | 0.00 |
| Gross بعد استبعاد الطلبين | 19,455,301.26 |
| Returns بعد استبعاد الإلغاءين | -474,039.74 |

## 7. مطابقة جدول customers مع عملاء صفوف البيع
| Item | Count |
|---|---|
| عملاء جدول customers | 5,875 |
| عملاء لديهم صفوف sale | 5,852 |
| في الجدول وبلا أي sale | 23 |
|   منهم لديهم cancellation | 23 |
|   منهم بلا sale ولا cancellation | 0 |

## 8. صفوف السعر الصفري مع Customer ID (ملاحظة D6)
| row_type | rows |
|---|---|
| fee_or_adjustment | 7 |
| other_non_product | 2 |
| zero_price_item | 61 |

## 9. المبيعات الشهرية (للتخطيط للمرحلة القادمة)
| month | orders | gross |
|---|---|---|

## 10. أعلى 10 دول حسب Gross
| country | gross | share |
|---|---|---|
| United Kingdom | 16,856,330.96 | 85.56% |
| Ireland | 623,795.85 | 3.17% |
| Netherlands | 549,775.06 | 2.79% |
| Germany | 383,847.67 | 1.95% |
| France | 311,288.38 | 1.58% |
| Australia | 167,867.51 | 0.85% |
| Spain | 97,818.07 | 0.5% |
| Switzerland | 94,046.89 | 0.48% |
| Sweden | 86,353.04 | 0.44% |
| Denmark | 67,422.69 | 0.34% |