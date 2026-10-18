# Step 3 - Products

## Sanity checks
| Check (sum over products) | Computed | Expected | Status |
|---|---|---|---|
| gross_sales | 19,700,954.46 | 19,700,954.46 | OK |
| returns_amount | -719,692.94 | -719,692.94 | OK |
| net_product_amount | 18,981,261.52 | 18,981,261.52 | OK |

## Concentration (Pareto, ranked by net revenue)
- Products sold (gross > 0, excluding dotcom codes): **4,709**
- Top 10 products = **7.6%** of net revenue; top 100 = **28.9%**
- 50% of net revenue comes from **289** products (6.1%)
- 80% of net revenue comes from **1,039** products (22.1%)
- Products with net revenue <= 0: 20
- Dotcom codes excluded: 16 products, gross 1,154.72 (0.006% of total gross)

## Top 15 products by net revenue (*D13 = affected by the cancelled mega-orders)
| net_rank | stock_code | product_description | net_product_amount | share_pct | cum_share_pct | units_sold | n_orders | n_customers | return_rate_pct |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 22423 | REGENCY CAKESTAND 3 TIER | 314513.47 | 1.66 | 1.66 | 26519.0 | 3918.0 | 1314.0 | 5.01 |
| 2 | 85123A | WHITE HANGING HEART T-LIGHT HOLDER | 252122.83 | 1.33 | 2.99 | 94839.0 | 5464.0 | 1490.0 | 3.59 |
| 3 | 85099B | JUMBO BAG RED RETROSPOT | 180830.85 | 0.95 | 3.94 | 97350.0 | 4013.0 | 978.0 | 1.19 |
| 4 | 47566 | PARTY BUNTING | 147157.43 | 0.78 | 4.71 | 28216.0 | 2674.0 | 894.0 | 0.83 |
| 5 | 84879 | ASSORTED COLOUR BIRD ORNAMENT | 128907.01 | 0.68 | 5.39 | 80293.0 | 2807.0 | 1010.0 | 0.6 |
| 6 | 22086 | PAPER CHAIN KIT 50'S CHRISTMAS | 116422.49 | 0.61 | 6.01 | 35126.0 | 2018.0 | 896.0 | 1.24 |
| 7 | 79321 | CHILLI LIGHTS | 80237.48 | 0.42 | 6.43 | 15918.0 | 1135.0 | 304.0 | 0.79 |
| 8 | 22197 | SMALL POPCORN HOLDER | 78935.92 | 0.42 | 6.84 | 88537.0 | 2322.0 | 601.0 | 0.78 |
| 9 | 22386 | JUMBO BAG PINK POLKADOT | 75518.22 | 0.4 | 7.24 | 39467.0 | 2245.0 | 601.0 | 1.14 |
| 10 | 84347 | ROTATING SILVER ANGELS T-LIGHT HLDR | 71031.15 | 0.37 | 7.62 | 31433.0 | 756.0 | 300.0 | 0.46 |
| 11 | 20725 | LUNCH BAG RED RETROSPOT | 70012.39 | 0.37 | 7.99 | 40506.0 | 3056.0 | 845.0 | 1.94 |
| 12 | 85099F | JUMBO BAG STRAWBERRY | 68595.97 | 0.36 | 8.35 | 37113.0 | 1855.0 | 549.0 | 0.74 |
| 13 | 48138 | DOORMAT UNION FLAG | 66778.78 | 0.35 | 8.7 | 10095.0 | 1664.0 | 678.0 | 0.54 |
| 14 | 23084 | RABBIT NIGHT LIGHT | 66756.59 | 0.35 | 9.05 | 30788.0 | 994.0 | 450.0 | 0.31 |
| 15 | 20685 | DOORMAT RED RETROSPOT | 65832.18 | 0.35 | 9.4 | 9789.0 | 1725.0 | 626.0 | 0.95 |

## Returns (overall return rate excluding D13 pairs: 2.44% of gross)
### Top 10 by return rate (products with >= 50 orders)
| net_rank | stock_code | product_description | gross_sales | returns_amount | return_rate_pct | n_orders |
|---|---|---|---|---|---|---|
| 4500 | 79323B | BLACK CHERRY LIGHTS | 1572.45 | -1557.2 | 99.03 | 58.0 |
| 2381 | 23113 | PANTRY CHOPPING BOARD | 5868.5 | -4803.06 | 81.84 | 57.0 |
| 1773 | 79341 | WILLOW BRANCH LIGHTS. | 4423.69 | -2519.6 | 56.96 | 79.0 |
| 2600 | 79323G | GOLD  CHERRY LIGHTS | 2007.88 | -1118.45 | 55.7 | 61.0 |
| 2363 | 79323S | SILVER CHERRY LIGHTS | 2084.32 | -997.05 | 47.84 | 56.0 |
| 2274 | 22903 | CALENDAR FAMILY FAVOURITES | 2053.96 | -880.0 | 42.84 | 82.0 |
| 2123 | 22920 | HERB MARKER BASIL | 2201.79 | -841.05 | 38.2 | 252.0 |
| 1344 | 85184D | S/4 BLUE ROUND DECOUPAGE BOXES | 4555.64 | -1664.92 | 36.55 | 67.0 |
| 1699 | 79323GR | GREEN CHERRY LIGHTS | 3209.36 | -1168.5 | 36.41 | 83.0 |
| 383 | 79323W | WHITE CHERRY LIGHTS | 18048.72 | -6421.1 | 35.58 | 349.0 |

### Top 10 by returned value
| net_rank | stock_code | product_description | gross_sales | returns_amount | return_rate_pct | n_orders |
|---|---|---|---|---|---|---|
| 1 | 22423 | REGENCY CAKESTAND 3 TIER | 331084.27 | -16570.8 | 5.01 | 3918.0 |
| 2 | 85123A | WHITE HANGING HEART T-LIGHT HOLDER | 261509.93 | -9387.1 | 3.59 | 5464.0 |
| 73 | 71477 | COLOUR GLASS. STAR T-LIGHT HOLDER | 44708.15 | -7164.12 | 16.02 | 809.0 |
| 220 | 21108 | FAIRY CAKE FLANNEL ASSORTED COLOUR | 25435.57 | -6614.37 | 26.0 | 613.0 |
| 383 | 79323W | WHITE CHERRY LIGHTS | 18048.72 | -6421.1 | 35.58 | 349.0 |
| 19 | 21843 | RED RETROSPOT CAKE STAND | 65189.95 | -5270.25 | 8.08 | 1527.0 |
| 68 | 84078A | SET/4 WHITE RETRO STORAGE CUBES | 43844.96 | -5187.65 | 11.83 | 328.0 |
| 2381 | 23113 | PANTRY CHOPPING BOARD | 5868.5 | -4803.06 | 81.84 | 57.0 |
| 61 | 48185 | DOORMAT FAIRY CAKE | 45777.19 | -4678.68 | 10.22 | 983.0 |
| 164 | 47566B | TEA TIME PARTY BUNTING | 27598.2 | -4490.5 | 16.27 | 874.0 |
