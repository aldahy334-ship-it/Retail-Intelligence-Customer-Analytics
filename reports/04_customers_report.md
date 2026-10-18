# Step 5 - Customers

## Sanity checks
| Check | Computed | Expected | Status |
|---|---|---|---|
| Customers in customers table | 5,875.00 | 5,875.00 | OK |
| Customers with at least one order | 5,852.00 | 5,852.00 | OK |
| Customers with cancellations only | 23.00 | 23.00 | OK |
| Orders | 39,516.00 | 39,516.00 | OK |
| Gross product sales (invoices) | 19,700,954.46 | 19,700,954.46 | OK |
| Returns (invoices) | -719,692.94 | -719,692.94 | OK |
| Net product revenue (invoices) | 18,981,261.52 | 18,981,261.52 | OK |
| Identified net: invoices vs customers.csv | 16,411,894.75 | 16,411,894.75 | OK |
| Identified orders: invoices vs customers.csv (n_orders) | 36,594.00 | 36,594.00 | OK |
| Snapshot date (last data day + 1) | 2011-12-10 | 2011-12-10 | OK |
| Customer 12346 gross (brief value is rounded, tol 1) | 77,352.96 | 77,353.00 | OK |
| Customer 12346 returns (brief value is rounded, tol 1) | -77,183.60 | -77,184.00 | OK |
| Customer 12346 net (brief value is rounded, tol 1) | 169.36 | 169.00 | OK |

- Customer IDs present in invoices but not in customers.csv: 67
- Snapshot date for Recency: 2011-12-10  (data ends 2011-12-09)

## Customer behaviour (identified customers with orders)
| Metric | Value |
|---|---|
| Customers with at least one order | 5,852 |
| One-time customers (1 order) | 27.6% |
| Repeat customers (2+ orders) | 72.4% |
| Median orders per customer | 3 |
| Median net revenue per customer | 842.44 |
| Mean net revenue per customer | 2,804.73 |
| Median days since last order | 96 |
| Customers with net revenue <= 0 | 19 |

## Revenue concentration (identified customers, ranked by net revenue)
| top_group | customers | net_revenue | share_of_identified_net_pct | share_of_total_net_pct |
|---|---|---|---|---|
| Top 1% | 59 | 5109807.34 | 31.13 | 26.92 |
| Top 5% | 293 | 8388625.07 | 51.11 | 44.19 |
| Top 10% | 586 | 10370749.91 | 63.19 | 54.64 |
| Top 20% | 1171 | 12591969.44 | 76.72 | 66.34 |

- 50% of identified net revenue comes from **274** customers (4.7%)
- 80% of identified net revenue comes from **1,381** customers (23.6%)

## RFM scores (score 5 = best; ranges computed from the data)
| score | R_days_since_last_order | F_orders | M_net_revenue | customers_R | customers_F | customers_M |
|---|---|---|---|---|---|---|
| 1 | 409 to 739 | 1 to 1 | -1,343 to 274 | 1171 | 1618 | 1171 |
| 2 | 187 to 409 | 2 to 2 | 274 to 594 | 1170 | 945 | 1170 |
| 3 | 59 to 187 | 3 to 4 | 594 to 1,182 | 1170 | 1148 | 1170 |
| 4 | 20 to 59 | 5 to 9 | 1,182 to 2,842 | 1170 | 1180 | 1170 |
| 5 | 1 to 20 | 10 to 373 | 2,843 to 578,409 | 1171 | 961 | 1171 |

## Segments: rules
| segment | rule |
|---|---|
| Champions | R >= 4 and F >= 4 |
| Loyal | R >= 3 and F >= 3 (not Champions) |
| New / Promising | R >= 4 and F <= 2 |
| Needs Attention | R = 3 and F <= 2 |
| At Risk | R <= 2 and F >= 3 |
| Hibernating | R <= 2 and F <= 2 |

- Rules are applied in the order Champions, Loyal, New / Promising, At Risk, Hibernating; the remainder is Needs Attention.

## Segments: summary
| segment | customers | customers_pct | net_revenue | net_share_pct | net_per_customer | median_orders | median_recency_days |
|---|---|---|---|---|---|---|---|
| Champions | 1389 | 23.74 | 11412742.46 | 69.53 | 8216.52 | 11.0 | 17.0 |
| Loyal | 1190 | 20.33 | 2453162.16 | 14.95 | 2061.48 | 4.0 | 72.0 |
| New / Promising | 510 | 8.71 | 270592.05 | 1.65 | 530.57 | 2.0 | 26.0 |
| Needs Attention | 422 | 7.21 | 224768.52 | 1.37 | 532.63 | 1.0 | 95.5 |
| At Risk | 710 | 12.13 | 1374002.72 | 8.37 | 1935.22 | 4.0 | 367.0 |
| Hibernating | 1631 | 27.87 | 678032.95 | 4.13 | 415.72 | 1.0 | 431.0 |

## Top 15 customers by net revenue (* = customer of a D13 mega-order)
| customer_id | country | orders | net_revenue | share_of_identified_net_pct | avg_order_value | last_order | recency_days | segment |
|---|---|---|---|---|---|---|---|---|
| 18102 | United Kingdom | 145 | 578408.64 | 3.52 | 4006.81 | 2011-12-09 | 1 | Champions |
| 14646 | Netherlands | 145 | 523202.74 | 3.19 | 3632.77 | 2011-12-08 | 2 | Champions |
| 14156 | Ireland | 144 | 297961.56 | 1.82 | 2105.95 | 2011-11-30 | 10 | Champions |
| 14911 | Ireland | 373 | 258601.47 | 1.58 | 730.28 | 2011-12-08 | 2 | Champions |
| 17450 | United Kingdom | 51 | 233803.91 | 1.42 | 4802.83 | 2011-12-01 | 9 | Champions |
| 13694 | United Kingdom | 143 | 190354.06 | 1.16 | 1368.12 | 2011-12-06 | 4 | Champions |
| 17511 | United Kingdom | 60 | 168504.44 | 1.03 | 2868.88 | 2011-12-07 | 3 | Champions |
| 12415 | Australia | 24 | 143107.02 | 0.87 | 6001.39 | 2011-11-15 | 25 | Champions |
| 16684 | United Kingdom | 55 | 141530.29 | 0.86 | 2675.32 | 2011-12-05 | 5 | Champions |
| 15061 | United Kingdom | 127 | 124982.13 | 0.76 | 995.18 | 2011-12-06 | 4 | Champions |
| 15311 | United Kingdom | 207 | 111625.03 | 0.68 | 554.84 | 2011-12-09 | 1 | Champions |
| 13089 | United Kingdom | 203 | 109983.57 | 0.67 | 559.15 | 2011-12-07 | 3 | Champions |
| 17949 | United Kingdom | 116 | 98469.06 | 0.6 | 929.6 | 2011-12-08 | 2 | Champions |
| 16029 | United Kingdom | 106 | 94890.63 | 0.58 | 1035.8 | 2011-11-01 | 39 | Champions |
| 14298 | United Kingdom | 82 | 90489.31 | 0.55 | 1112.13 | 2011-12-01 | 9 | Champions |

## Customer 12346 and the D13 customers: gross rank vs net rank
| customer_id | orders | gross_sales | returns_amount | net_revenue | n_cancel_invoices | rank_by_gross | rank_by_net | segment |
|---|---|---|---|---|---|---|---|---|
| 12346 | 3 | 77352.96 | -77183.6 | 169.36 | 1 | 19 | 5194 | At Risk |
| 16446 | 2 | 168472.5 | -168469.6 | 2.9 | 1 | 8 | 5832 | New / Promising |

- Invoice 581483: customer 16446
- Invoice 541431: customer 12346

## Anonymous orders: how much revenue does the customer analysis not see?
| group | orders | orders_pct | gross_sales | net_revenue | net_share_pct | median_order_value | mean_order_value_ex_d13 |
|---|---|---|---|---|---|---|---|
| Identified | 36594 | 92.61 | 17124941.0 | 16411894.75 | 86.46 | 303.1 | 461.28 |
| Anonymous (no Customer ID) | 2922 | 7.39 | 2576013.46 | 2569366.77 | 13.54 | 184.48 | 881.59 |

- Net revenue per group includes the cancellation invoices of that group.
- mean_order_value_ex_d13 excludes invoices 581483 and 541431.
