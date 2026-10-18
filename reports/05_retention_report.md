# Step 6 - Cohorts and retention

## Sanity checks
| Check | Computed | Expected | Status |
|---|---|---|---|
| Customers with at least one order | 5,852.00 | 5,852.00 | OK |
| Customers with 2+ orders (5,852 minus 1,618 with F=1 in step 5) | 4,234.00 | 4,234.00 | OK |
| Orders of identified customers | 36,594.00 | 36,594.00 | OK |
| Net revenue of customers with orders (all months) | 16,413,300.88 | 16,413,300.86 | DIFF |
| Replicates step 5 at 2011-12-10: Champions customers | 1,389.00 | 1,389.00 | OK |
| Replicates step 5 at 2011-12-10: Champions net revenue | 11,412,742.46 | 11,412,742.46 | OK |
| Replicates step 5 at 2011-12-10: At Risk customers | 710.00 | 710.00 | OK |
| International net P1 (step 4) | 1,269,189.62 | 1,269,189.62 | OK |
| International net P2 (step 4) | 1,448,937.58 | 1,448,937.58 | OK |
| Biggest accounts found (NL / IE / AU) match step 5 | {'Netherlands': [14646], 'Ireland': [14156, 14911], 'Australia': [12415]} | {'Netherlands': [14646], 'Ireland': [14156, 14911], 'Australia': [12415]} | OK |

- Last complete month: 2011-11; last data day: 2011-12-09; partial months excluded: ['2011-12']
- Base cohort = 2009-12 (951 customers): data starts here, so it includes customers who already existed
- Customers whose first order is in a partial month (no retention yet): 28
- Net revenue booked before a customer's first order month (returns of earlier purchases, put in month 0): -3,325.17

## Cohort summary (monthly active %, complete months only)
| cohort | customers | M1_active_pct | M2_active_pct | M3_active_pct | M6_active_pct | M9_active_pct | M12_active_pct |
|---|---|---|---|---|---|---|---|
| 2009-12 (base) | 951 | 35.0 | 33.3 | 42.5 | 37.6 | 36.2 | 37.6 |
| 2010-01 | 368 | 21.5 | 32.1 | 31.5 | 26.9 | 32.6 | 22.8 |
| 2010-02 | 375 | 23.5 | 22.7 | 29.3 | 19.2 | 27.7 | 15.2 |
| 2010-03 | 441 | 19.0 | 23.1 | 24.3 | 24.7 | 10.9 | 20.0 |
| 2010-04 | 294 | 19.0 | 19.0 | 16.0 | 27.6 | 10.9 | 14.3 |
| 2010-05 | 255 | 15.7 | 16.9 | 17.6 | 21.2 | 8.2 | 15.3 |
| 2010-06 | 267 | 17.6 | 18.7 | 20.6 | 12.7 | 11.2 | 15.0 |
| 2010-07 | 185 | 15.7 | 18.4 | 29.7 | 11.4 | 11.4 | 13.0 |
| 2010-08 | 163 | 19.6 | 28.8 | 32.5 | 9.8 | 12.9 | 14.7 |
| 2010-09 | 239 | 23.0 | 23.4 | 13.0 | 13.8 | 13.0 | 22.6 |
| 2010-10 | 375 | 25.9 | 14.7 | 12.5 | 13.1 | 9.3 | 19.2 |
| 2010-11 | 326 | 17.5 | 9.5 | 9.5 | 12.9 | 9.2 | 25.2 |
| 2010-12 | 76 | 9.2 | 5.3 | 9.2 | 5.3 | 2.6 |  |
| 2011-01 | 72 | 16.7 | 22.2 | 19.4 | 15.3 | 20.8 |  |
| 2011-02 | 125 | 16.0 | 16.0 | 18.4 | 16.0 | 18.4 |  |
| 2011-03 | 179 | 17.9 | 21.8 | 20.1 | 20.7 |  |  |
| 2011-04 | 106 | 24.5 | 19.8 | 19.8 | 17.9 |  |  |
| 2011-05 | 111 | 23.4 | 24.3 | 16.2 | 26.1 |  |  |
| 2011-06 | 108 | 23.1 | 21.3 | 26.9 |  |  |  |
| 2011-07 | 101 | 20.8 | 29.7 | 27.7 |  |  |  |
| 2011-08 | 107 | 26.2 | 29.9 | 26.2 |  |  |  |
| 2011-09 | 188 | 27.1 | 37.8 |  |  |  |  |
| 2011-10 | 221 | 31.7 |  |  |  |  |  |
| 2011-11 | 191 |  |  |  |  |  |  |

## Average monthly retention (size-weighted, only cohorts observable at that month)
| months_since_first | new_cohorts_active_pct | new_cohorts_n | base_active_pct |
|---|---|---|---|
| 1 | 21.0 | 22 | 35.0 |
| 2 | 21.5 | 21 | 33.3 |
| 3 | 21.1 | 20 | 42.5 |
| 6 | 18.4 | 17 | 37.6 |
| 9 | 15.0 | 14 | 36.2 |
| 12 | 18.4 | 11 | 37.6 |

## Repeat purchase: a later-day order within N days (only fully observable customers)
| window_days | new_cohorts_eligible | new_cohorts_repeat_pct | base_cohort_eligible | base_cohort_repeat_pct |
|---|---|---|---|---|
| 30 | 4749 | 17.1 | 951 | 29.1 |
| 60 | 4547 | 31.6 | 951 | 49.6 |
| 90 | 4305 | 40.9 | 951 | 59.3 |
| 180 | 4001 | 56.5 | 951 | 77.5 |
| 365 | 3334 | 69.7 | 951 | 89.4 |

- Customers with 2+ invoices but no order on a later day (same-day invoices only): 55
- Median days to the second order among new-cohort customers who repeated: 67

## Repeat rate by cohort quarter (blank = window not fully observable; * = base)
| cohort_quarter | customers | repeat_30d_pct | repeat_60d_pct | repeat_90d_pct | repeat_180d_pct | repeat_365d_pct |
|---|---|---|---|---|---|---|
| 2009Q4* | 951 | 29.1 | 49.6 | 59.3 | 77.5 | 89.4 |
| 2010Q1 | 1184 | 14.7 | 33.8 | 46.8 | 65.9 | 80.3 |
| 2010Q2 | 816 | 14.2 | 26.0 | 35.5 | 59.6 | 70.3 |
| 2010Q3 | 587 | 16.7 | 32.9 | 45.0 | 55.9 | 65.8 |
| 2010Q4 | 777 | 19.3 | 29.3 | 32.7 | 42.1 |  |
| 2011Q1 | 376 | 16.8 | 26.6 | 37.2 | 51.3 |  |
| 2011Q2 | 325 | 16.9 | 33.2 | 41.5 |  |  |
| 2011Q3 | 396 | 20.5 | 41.2 |  |  |  |
| 2011Q4 | 440 |  |  |  |  |  |

## Repeat rate by how the customer was acquired (new cohorts)
| group (new cohorts) | eligible_180d | repeat_180d_pct | eligible_365d | repeat_365d_pct |
|---|---|---|---|---|
| Acquired Sep-Nov (peak season) | 940 | 45.1 | 940 | 57.7 |
| Acquired Dec-Aug | 3061 | 59.9 | 2394 | 74.5 |
| First order from UK | 3641 | 56.3 | 3051 | 69.5 |
| First order from abroad | 360 | 57.8 | 283 | 72.8 |

- Groups differ in which calendar months are observable, so compare them with care.

## Cumulative net revenue per acquired customer (GBP)
| months_since_first | new_cohorts_gbp | new_cohorts_n | base_gbp |
|---|---|---|---|
| 0 | 453.3 | 23 | 699.6 |
| 1 | 541.5 | 22 | 1089.7 |
| 3 | 730.5 | 20 | 1779.2 |
| 6 | 978.1 | 17 | 2693.1 |
| 9 | 1242.3 | 14 | 3726.7 |
| 12 | 1512.7 | 11 | 5126.2 |

## Appendix A - customer IDs in invoices.csv but not in customers.csv (open from step 5)
| invoice_type | invoices | customers | net_product_amount | shipping_amount | fee_adjustment_amount |
|---|---|---|---|---|---|
| non_sale | 120 | 67 | 0.0 | 241.0 | -78505.78 |

## Appendix B - RFM segments at other snapshot dates (is Recency flattered by the season?)
| segment | 2010-12-10 customers % | 2010-12-10 net % | 2011-09-01 customers % | 2011-09-01 net % | 2011-12-10 customers % | 2011-12-10 net % |
|---|---|---|---|---|---|---|
| Champions | 19.7 | 62.3 | 23.7 | 70.5 | 23.7 | 69.5 |
| Loyal | 17.8 | 15.4 | 18.3 | 13.3 | 20.3 | 14.9 |
| New / Promising | 11.8 | 3.1 | 9.2 | 1.9 | 8.7 | 1.6 |
| Needs Attention | 10.7 | 2.8 | 8.9 | 1.6 | 7.2 | 1.4 |
| At Risk | 10.7 | 10.1 | 10.9 | 7.7 | 12.1 | 8.4 |
| Hibernating | 29.3 | 6.3 | 29.1 | 5.0 | 27.9 | 4.1 |
| customers scored | 4,285 |  | 5,224 |  | 5,852 |  |
| R>=4 means last order within (days) | 36 |  | 105 |  | 59 |  |

- Same rules as step 5; for each date only orders before that date are used.

## Appendix C - international growth with and without the biggest accounts (P1 = Dec09-Nov10, P2 = Dec10-Nov11)
| market | key_accounts | total_P1 | total_P2 | total_change_pct | key_P1 | key_P2 | ex_key_P1 | ex_key_P2 | ex_key_change_pct |
|---|---|---|---|---|---|---|---|---|---|
| Netherlands | 14646 | 262618.0 | 271752.0 | +3.5% | 244425.0 | 267050.0 | 18193.0 | 4702.0 | -74.2% |
| Ireland | 14156, 14911 | 343744.0 | 252540.0 | -26.5% | 313826.0 | 235911.0 | 29918.0 | 16629.0 | -44.4% |
| Australia | 12415 | 29360.0 | 136990.0 | +366.6% | 19469.0 | 123638.0 | 9891.0 | 13352.0 | +35.0% |
| International (all) | 14646, 14156, 14911, 12415 | 1269190.0 | 1448938.0 | +14.2% | 577719.0 | 626599.0 | 691470.0 | 822338.0 | +18.9% |

- Biggest accounts = top customers by net revenue inside each country (invoice country).
- International (all) removes all of those accounts together.
