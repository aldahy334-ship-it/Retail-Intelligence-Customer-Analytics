# Step 7 - Returns and cancellations

## Sanity checks
| Check | Computed | Expected | Status |
|---|---|---|---|
| Gross product sales | 19,700,954.46 | 19,700,954.46 | OK |
| Returns (cancellation lines) | -719,692.94 | -719,692.94 | OK |
| Cancellation lines | 17,974.00 | 17,974.00 | OK |
| Cancellation invoices | 7,406.00 | 7,406.00 | OK |
| Cancellation lines with Customer ID (%) | 98.15 | 98.20 | OK |
| D13 cancellations (C581484 + C541433) | -245,653.20 | -245,653.20 | OK |
| Returns excluding D13 | -474,039.74 | -474,039.74 | OK |
| Gross excluding D13 | 19,455,301.26 | 19,455,301.26 | OK |
| Returns: invoices.csv vs sales_lines | -719,692.94 | -719,692.94 | OK |
| Net of cancellation-only customers (explains step 5 vs 6 gap) | -1,406.13 | -1,406.13 | OK |

- Overall return rate excluding D13 pairs: **2.44%** of gross (474,039.74 of 19,455,301.26)

## Returns over time (booked in the month of the cancellation, D13 pairs excluded)
| period | gross | returns_abs | return_rate_pct | cancel_invoices | cancel_inv_per_100_orders |
|---|---|---|---|---|---|
| Dec09-Nov10 | 9429521.39 | 240968.76 | 2.56 | 3984 | 20.18 |
| Dec10-Nov11 | 9578756.19 | 227413.82 | 2.37 | 3284 | 17.32 |

- Sep-Nov months: return rate 2.49% vs other months 2.45% (complete months)
- Highest monthly return rate: 2011-04 (6.45%); lowest: 2011-05 (1.21%)
- Partial months excluded: ['2011-12']

### Monthly table
| month | gross | returns | return_rate_pct | cancel_invoices | orders | cancel_inv_per_100_orders | partial |
|---|---|---|---|---|---|---|---|
| 2009-12 | 801102.97 | -19561.28 | 2.44 | 379 | 1666 | 22.75 |  |
| 2010-01 | 613850.81 | -7465.63 | 1.22 | 241 | 1049 | 22.97 |  |
| 2010-02 | 539744.69 | -12584.39 | 2.33 | 219 | 1189 | 18.42 |  |
| 2010-03 | 764333.85 | -9657.20 | 1.26 | 351 | 1647 | 21.31 |  |
| 2010-04 | 648993.82 | -10025.26 | 1.54 | 263 | 1435 | 18.33 |  |
| 2010-05 | 645645.39 | -37294.14 | 5.78 | 387 | 1484 | 26.08 |  |
| 2010-06 | 699316.02 | -26380.61 | 3.77 | 319 | 1612 | 19.79 |  |
| 2010-07 | 634896.99 | -17132.73 | 2.70 | 314 | 1507 | 20.84 |  |
| 2010-08 | 676060.72 | -12418.65 | 1.84 | 242 | 1402 | 17.26 |  |
| 2010-09 | 871878.34 | -27777.97 | 3.19 | 319 | 1789 | 17.83 |  |
| 2010-10 | 1098017.67 | -25550.02 | 2.33 | 406 | 2244 | 18.09 |  |
| 2010-11 | 1435680.12 | -35120.88 | 2.45 | 544 | 2719 | 20.01 |  |
| 2010-12 | 777931.77 | -17607.86 | 2.26 | 301 | 1550 | 19.42 |  |
| 2011-01 | 594749.59 | -14342.70 | 2.41 | 246 | 1080 | 22.78 |  |
| 2011-02 | 508886.20 | -8375.87 | 1.65 | 191 | 1093 | 17.47 |  |
| 2011-03 | 691257.61 | -10675.30 | 1.54 | 281 | 1440 | 19.51 |  |
| 2011-04 | 516218.12 | -33316.91 | 6.45 | 220 | 1235 | 17.81 |  |
| 2011-05 | 741192.41 | -8948.23 | 1.21 | 267 | 1668 | 16.01 |  |
| 2011-06 | 738751.87 | -13760.84 | 1.86 | 299 | 1525 | 19.61 |  |
| 2011-07 | 689364.41 | -11409.21 | 1.66 | 236 | 1452 | 16.25 |  |
| 2011-08 | 725513.50 | -22929.52 | 3.16 | 240 | 1339 | 17.92 |  |
| 2011-09 | 1030475.36 | -17044.68 | 1.65 | 299 | 1818 | 16.45 |  |
| 2011-10 | 1106669.82 | -43992.16 | 3.98 | 308 | 2005 | 15.36 |  |
| 2011-11 | 1457745.53 | -25010.54 | 1.72 | 396 | 2751 | 14.39 |  |
| 2011-12 | 447023.67 | -5657.16 | 1.27 | 136 | 815 | 16.69 | partial |

## Size of cancellation invoices (D13 excluded)
| metric | value |
|---|---|
| Cancellation invoices | 7404.00 |
| Median value | 15.90 |
| Mean value | 64.02 |
| 90th percentile value | 83.99 |
| Median lines per invoice | 1.00 |
| Share of invoices under 50 (%) | 82.79 |
| Top 10 invoices, share of returned value (%) | 17.58 |

## Who returns: customers (identified customers with a cancellation)
- Customers with at least one cancellation: **2,443** = 41.7% of 5,852 buyers
- 50% of identified returned value comes from **45** customers (1.8% of returners)
- Median customer return rate (returned / own gross): 2.1%
| group | customers | returned_value | share_of_identified_returns_pct |
|---|---|---|---|
| Top 1% | 24 | 191261.43 | 40.92 |
| Top 5% | 122 | 296710.49 | 63.48 |
| Top 10% | 244 | 343876.07 | 73.57 |
| Top 20% | 489 | 392211.71 | 83.91 |

### Top 10 customers by returned value
| customer_id | returned_value | country | gross | return_rate_pct | cancel_invoices |
|---|---|---|---|---|---|
| 15749 | 22998.40 | United Kingdom | 44534.30 | 51.64 | 1 |
| 12931 | 20800.37 | United Kingdom | 92347.34 | 22.52 | 11 |
| 16029 | 14904.24 | United Kingdom | 109794.87 | 13.57 | 6 |
| 14911 | 13791.56 | Ireland | 272393.03 | 5.06 | 93 |
| 14277 | 12829.34 | France | 16817.36 | 76.29 | 5 |
| 12454 | 12360.82 | Spain | 16459.78 | 75.10 | 3 |
| 17450 | 11140.34 | United Kingdom | 244944.25 | 4.55 | 4 |
| 16754 | 10807.25 | United Kingdom | 65500.07 | 16.50 | 5 |
| 17949 | 9364.42 | United Kingdom | 107833.48 | 8.68 | 12 |
| 16684 | 5612.48 | United Kingdom | 147142.77 | 3.81 | 9 |

## Anonymous cancellations (no Customer ID)
- 332 lines, 123 invoices, returned value 6,646.69 = 1.4% of returns

## UK vs International
| market | gross | returns_abs | return_rate_pct |
|---|---|---|---|
| UK | 16610677.76 | 389596.46 | 2.35 |
| International | 2844623.50 | 84443.28 | 2.97 |

## Concentration of returned value by product
- Products with any return: 2,885; top 10 = 14.9%, top 100 = 45.7% of returned value
- 50% of returned value comes from 124 products

## Customer-product matching (no invoice link, so this is a customer-level test)
A return line is an 'orphan' when that customer has no purchase of that product code anywhere in the data. Purchases before 2009-12 are invisible, so some orphans are expected.
| group | return_lines | returned_value | orphan_value_pct |
|---|---|---|---|
| All products | 17640 | 467393.05 | 4.69 |
| Family 79323* | 404 | 17885.20 | 28.24 |
| All other products | 17236 | 449507.85 | 3.75 |

## Time from the customer's latest earlier purchase of the same product to the return
- Return lines with an earlier purchase of that product by that customer: 16,108 of 17,640 (91.3%)
- Median 10 days; 75th percentile 30; 90th percentile 83
- Within 30 days: 74.7%; within 90 days: 90.8%
- Caveat: this is the latest earlier purchase, not necessarily the one being returned.

## Family 79323* (Cherry Lights): is the high return rate a coding artefact?
Hypothesis from step 3: either real defects, or colours entered under the wrong code. Test: for returned value of one colour, how often did the same customer buy a DIFFERENT 79323* colour but never this one (other_color_bought_pct)?
- Family combined: gross 49,191.85, returns 17,986.45, return rate 36.56% (store-wide 2.44%)
- Family returned value where the customer never bought ANY 79323* code: 2.8% (vs 28.2% at single-code level)
| stock_code | description | gross | returns_abs | return_rate_pct | sale_orders | return_customers | orphan_value_pct | other_color_bought_pct |
|---|---|---|---|---|---|---|---|---|
| 79323B | BLACK CHERRY LIGHTS | 1572.45 | 1557.20 | 99.03 | 58 | 48 | 62.25 | 61.80 |
| 79323G | GOLD  CHERRY LIGHTS | 2007.88 | 1118.45 | 55.70 | 61 | 19 | 33.67 | 33.67 |
| 79323GR | GREEN CHERRY LIGHTS | 3209.36 | 1168.50 | 36.41 | 83 | 34 | 39.31 | 39.31 |
| 79323LP | LIGHT PINK CHERRY LIGHTS | 8481.19 | 2702.80 | 31.87 | 170 | 55 | 23.31 | 15.98 |
| 79323P | PINK CHERRY LIGHTS | 13787.93 | 4021.35 | 29.17 | 265 | 78 | 13.18 | 11.03 |
| 79323S | SILVER CHERRY LIGHTS | 2084.32 | 997.05 | 47.84 | 56 | 19 | 74.18 | 71.45 |
| 79323W | WHITE CHERRY LIGHTS | 18048.72 | 6421.10 | 35.58 | 349 | 109 | 21.72 | 18.86 |

## Highest return rates outside the 79323* family (products with >= 50 orders)
- top_customer_pct: share of this product's identified returned value from its single biggest returner.
| stock_code | description | gross | returns_abs | return_rate_pct | orders | return_customers | top_customer_pct | orphan_value_pct |
|---|---|---|---|---|---|---|---|---|
| 23113 | PANTRY CHOPPING BOARD | 5868.50 | 4803.06 | 81.84 | 57 | 5 | 99.59 | 0.00 |
| 79341 | WILLOW BRANCH LIGHTS. | 4423.69 | 2519.60 | 56.96 | 79 | 22 | 67.49 | 19.80 |
| 22903 | CALENDAR FAMILY FAVOURITES | 2053.96 | 880.00 | 42.84 | 82 | 1 | 100.00 | 0.00 |
| 22920 | HERB MARKER BASIL | 2201.79 | 841.05 | 38.20 | 252 | 2 | 99.07 | 0.00 |
| 85184D | S/4 BLUE ROUND DECOUPAGE BOXES | 4555.64 | 1664.92 | 36.55 | 67 | 2 | 99.29 | 0.00 |
| 37423 | WHITE WITH BLACK CATS PLATE | 843.88 | 295.20 | 34.98 | 70 | 1 | 100.00 | 0.00 |
| 21096 | SET/6 FRUIT SALAD  PAPER PLATES | 2715.96 | 911.04 | 33.54 | 143 | 1 | 100.00 | 0.00 |
| 84247N | PACK/12 BLUE FOLKART CARDS | 297.48 | 97.35 | 32.72 | 53 | 3 | 33.33 | 0.00 |
| 22341 | LOVE GARLAND PAINTED ZINC | 5702.19 | 1858.20 | 32.59 | 240 | 7 | 96.09 | 1.15 |
| 16046 | TEATIME PEN CASE & PENS | 1226.90 | 389.04 | 31.71 | 59 | 2 | 94.76 | 5.24 |

