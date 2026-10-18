# Phase B report (steps 5-10)
runtime 19s | lines_all rows: 1,044,848

## Tables built
```
          table    rows
    sales_lines 1033062
non_sales_lines   11786
       invoices   53628
      customers    5875
       products    4739
       calendar     739
```

## non_sales_lines by type
```
         row_type  rows
 stock_adjustment  5913
         shipping  3788
fee_or_adjustment  1906
other_non_product   118
  zero_price_item    61
```

## invoices by type
```
invoice_type  invoices
        sale     39516
cancellation      7406
    non_sale      6706
```
- invoices without Customer ID: 8,752 (16.3%)
- invoices whose lines had >1 timestamp (earliest used): 83

## Sensitivity: exact duplicates kept vs removed (product-only figures)
```
             metric  with_duplicates  without_duplicates  difference  difference_pct
         sale_lines       1015088.00          1003357.00    11731.00            1.16
             orders         39516.00            39516.00        0.00            0.00
          customers          5852.00             5852.00        0.00            0.00
         units_sold      11221957.00         11188061.00    33896.00            0.30
        gross_sales      19700954.46         19643861.64    57092.82            0.29
            returns       -719692.94          -716462.57    -3230.37            0.45
net_product_revenue      18981261.52         18927399.07    53862.45            0.28
    avg_order_value           498.56              497.11        1.44            0.29
```

## Outlier flags (flag only, nothing removed)
- rule: abs(quantity) or abs(line amount) above the 99.900% percentile of SALE lines
- quantity threshold: 500 | amount threshold: 750.00
- flagged lines: quantity=1,104, amount=1,073
- 10 largest sale lines by quantity:
```
invoice stock_code                        description  quantity  price  customer_id
 581483      23843        PAPER CRAFT , LITTLE BIRDIE     80995   2.08        16446
 541431      23166     MEDIUM CERAMIC TOP STORAGE JAR     74215   1.04        12346
 497946      37410 BLACK AND WHITE PAISLEY FLOWER MUG     19152   0.10        13902
 501534      21099        SET/6 STRAWBERRY PAPER CUPS     12960   0.10        13902
 501534      21091        SET/6 WOODLAND PAPER PLATES     12960   0.10        13902
 501534      21085          SET/6 WOODLAND PAPER CUPS     12744   0.10        13902
 501534      21092      SET/6 STRAWBERRY PAPER PLATES     12480   0.10        13902
 502269      21984    PACK OF 12 PINK PAISLEY TISSUES     10000   0.25        17940
 502269      21982            PACK OF 12 SUKI TISSUES     10000   0.25        17940
 502269      21980      PACK OF 12 RED SPOTTY TISSUES     10000   0.25        17940
```

## Customers
- customers: 5,875 | with at least one order: 5,852 | with >1 country: 12

## Calendar
- range: 2009-12-01 to 2011-12-09 | partial months: ['2011-12']
```
  weekday  invoices
 Thursday     11335
  Tuesday     10299
Wednesday      9597
   Monday      8595
   Friday      8505
   Sunday      5265
 Saturday        32
```

## Country map (full list - please review)
```
         country_raw   rows  invoices        country_clean  is_generic_label
      United Kingdom 959983     49108       United Kingdom             False
                EIRE  17689       806              Ireland             False
             Germany  17363      1095              Germany             False
              France  14059       746               France             False
         Netherlands   5138       250          Netherlands             False
               Spain   3766       188                Spain             False
         Switzerland   3183       123          Switzerland             False
             Belgium   3111       183              Belgium             False
            Portugal   2540       124             Portugal             False
           Australia   1891       117            Australia             False
     Channel Islands   1647        79      Channel Islands             False
               Italy   1509        92                Italy             False
              Sweden   1364       129               Sweden             False
              Norway   1308        53               Norway             False
              Cyprus   1176        45               Cyprus             False
             Finland   1049        68              Finland             False
             Austria    938        51              Austria             False
             Denmark    797        53              Denmark             False
         Unspecified    756        28          Unspecified              True
              Greece    663        21               Greece             False
               Japan    565        56                Japan             False
                 USA    535        25        United States             False
              Poland    527        38               Poland             False
United Arab Emirates    500        22 United Arab Emirates             False
              Israel    371        11               Israel             False
           Hong Kong    364        21            Hong Kong             False
           Singapore    346        14            Singapore             False
               Malta    299        16                Malta             False
              Canada    228         8               Canada             False
             Iceland    222         8              Iceland             False
                 RSA    169         5         South Africa             False
           Lithuania    154         6            Lithuania             False
             Bahrain    126        12              Bahrain             False
              Brazil     94         2               Brazil             False
            Thailand     76         2             Thailand             False
               Korea     63         3                Korea             False
  European Community     61         5   European Community              True
             Lebanon     58         3              Lebanon             False
         West Indies     54         1          West Indies             False
             Bermuda     34         1              Bermuda             False
             Nigeria     32         3              Nigeria             False
      Czech Republic     30         5       Czech Republic             False
        Saudi Arabia     10         2         Saudi Arabia             False
```

## Checks
- [PASS] every line in exactly one table (sales + non-sales = all): 1,033,062 + 11,786 vs 1,044,848
- [PASS] invoices: one row per invoice: 53,628 rows
- [PASS] products: one row per stock code: 4,739 rows
- [PASS] customers: one row per customer: 5,875 rows
- [PASS] no invoice with >1 customer or >1 country: 0 customer / 0 country
- [PASS] invoice gross sales = line gross sales: 19,700,954.46
- [PASS] product gross sales = line gross sales: 19,700,954.46
- [PASS] customer net + no-customer net = total net: 18,981,261.52 vs 18,981,261.52
- [PASS] calendar covers every invoice day: 
- [PASS] sale lines all have quantity > 0 and price > 0: 