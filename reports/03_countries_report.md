# Step 4 - Markets

## Sanity checks
| Check | Computed | Expected | Status |
|---|---|---|---|
| Net revenue | 18,981,261.52 | 18,981,261.52 | OK |
| Orders | 39,516.00 | 39,516.00 | OK |
| Net revenue P1 (step 2) | 9,188,552.63 | 9,188,552.60 | OK |
| Net revenue P2 (step 2) | 9,351,342.37 | 9,351,342.40 | OK |

## UK vs International (whole period)
| market | net_revenue | share_pct | orders | customers | median_order_value | mean_order_value_ex_d13 | anon_orders_pct |
|---|---|---|---|---|---|---|---|
| UK | 16221081.3 | 85.46 | 36184 | 5334 | 296.76 | 459.09 | 7.8 |
| International | 2760180.22 | 14.54 | 3332 | 518 | 421.65 | 853.73 | 3.0 |

## Top 15 countries by net revenue (* = generic label, see D14)
| country | net_revenue | orders | customers | median_order_value | mean_order_value_ex_d13 | anon_orders_pct | top_customer_share_pct | share_pct | cum_share_pct |
|---|---|---|---|---|---|---|---|---|---|
| United Kingdom | 16221081.3 | 36184 | 5334 | 296.76 | 459.09 | 7.8 | 3.57 | 85.46 | 85.46 |
| Ireland | 603407.1 | 581 | 3 | 694.66 | 1073.66 | 9.12 | 49.38 | 3.18 | 88.64 |
| Netherlands | 546097.08 | 216 | 22 | 657.08 | 2545.25 | 0.0 | 95.81 | 2.88 | 91.51 |
| Germany | 375132.18 | 753 | 107 | 360.3 | 509.76 | 0.0 | 8.89 | 1.98 | 93.49 |
| France | 293626.34 | 598 | 93 | 360.06 | 520.55 | 1.34 | 10.95 | 1.55 | 95.04 |
| Australia | 166349.65 | 89 | 15 | 394.59 | 1886.15 | 0.0 | 86.03 | 0.88 | 95.91 |
| Switzerland | 92940.36 | 85 | 22 | 507.24 | 1106.43 | 3.53 | 24.84 | 0.49 | 96.4 |
| Spain | 84862.88 | 144 | 38 | 364.37 | 679.29 | 0.0 | 22.58 | 0.45 | 96.85 |
| Sweden | 84379.07 | 99 | 19 | 376.0 | 872.25 | 1.01 | 54.35 | 0.44 | 97.3 |
| Denmark | 63355.59 | 42 | 12 | 703.74 | 1605.3 | 0.0 | 47.94 | 0.33 | 97.63 |
| Belgium | 56618.39 | 143 | 29 | 301.56 | 398.69 | 0.0 | 12.67 | 0.3 | 97.93 |
| Portugal | 46776.59 | 85 | 23 | 359.52 | 557.73 | 2.35 | 20.91 | 0.25 | 98.17 |
| Channel Islands | 41851.71 | 54 | 13 | 833.8 | 815.56 | 0.0 | 29.58 | 0.22 | 98.39 |
| Japan | 39746.77 | 33 | 10 | 320.08 | 1303.75 | 0.0 | 52.89 | 0.21 | 98.6 |
| Norway | 38413.68 | 39 | 12 | 477.07 | 989.11 | 0.0 | 43.72 | 0.2 | 98.81 |

## Growth: Dec10-Nov11 vs Dec09-Nov10 (countries with >= 25,000 in the first period)
| market | P1 | P2 | change_pct |
|---|---|---|---|
| UK | 7919363.01 | 7902404.79 | -0.2% |
| International | 1269189.62 | 1448937.58 | +14.2% |
| Total | 9188552.63 | 9351342.37 | +1.8% |
| Netherlands | 262617.54 | 271751.52 | +3.5% |
| Ireland | 343743.64 | 252540.42 | -26.5% |
| Germany | 174323.78 | 193963.7 | +11.3% |
| France | 111462.95 | 175772.12 | +57.7% |
| Australia | 29359.65 | 136990.0 | +366.6% |
| Switzerland | 40435.01 | 52505.35 | +29.9% |
| Spain | 33097.68 | 51521.77 | +55.7% |
| Sweden | 49202.16 | 35176.91 | -28.5% |
| Denmark | 45313.45 | 17891.24 | -60.5% |

## International share of net revenue
- Dec09-Nov10: **13.8%** | Dec10-Nov11: **15.5%**
- Monthly range (complete months): 8.8% to 21.3%
- Countries in data: 43 | countries covering 90% of net revenue: 3
