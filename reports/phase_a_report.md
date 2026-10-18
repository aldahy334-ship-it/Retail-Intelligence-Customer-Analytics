# Phase A report (steps 0-4)
- source: `online_retail_II.xlsx` | unchanged after run: **True** | runtime 105s
- sheets: ['Year 2009-2010', 'Year 2010-2011']

## Row-count waterfall
- rows loaded (both sheets): 1,067,371
- shared invoices (identical in both sheets): 1,088
- overlap rows removed (copy from sheet 2): 22,523
- rows after overlap resolution: 1,044,848
- exact duplicate rows FLAGGED (kept): 11,812

## Rows by row_type
```
         row_type    rows  invoices    units      amount  pct_with_customer  exact_dup_rows  share_pct
             sale 1015088     39516 11221957 19700954.46               77.6           11731      97.15
     cancellation   17974      7406  -469882  -719692.94               98.2              59       1.72
 stock_adjustment    5913      5279  -340387        0.00                0.0              10       0.57
         shipping    3788      3783    13639   433410.51               59.5               0       0.36
fee_or_adjustment    1906      1697     1461  -506800.02               72.6              12       0.18
other_non_product     118       111      320     1890.11               13.6               0       0.01
  zero_price_item      61        52    14736        0.00              100.0               0       0.01
```
(amount = Quantity x Price, descriptive only, NOT a result)

### stock codes captured as `shipping`
```
value  rows
 POST  2086
  DOT  1425
   C2   277
```

### stock codes captured as `fee_or_adjustment`
```
       value  rows
           M  1403
           D   173
           S   102
BANK CHARGES   100
      ADJUST    67
   AMAZONFEE    36
        CRUK    16
           B     6
     ADJUST2     3
```

### stock codes captured as `other_non_product`
```
       value  rows
GIFT_0001_20    29
GIFT_0001_30    29
GIFT_0001_10    16
     TEST001    15
GIFT_0001_50     8
GIFT_0001_40     7
GIFT_0001_80     4
GIFT_0001_70     3
     TEST002     2
GIFT_0001_60     2
GIFT_0001_90     2
        GIFT     1
```

## stock_adjustment (zero price, no customer)
```
 qty_sign  rows
       -1  3392
        1  2521
```
top descriptions, quantity < 0:
```
                 value  rows
             <missing>  2632
                 check   121
               damages    83
                     ?    81
               damaged    78
               missing    27
 sold as set on dotcom    20
               Damaged    17
               smashed     9
           thrown away     9
Unsaleable, destroyed.     9
                dotcom     8
```
top descriptions, quantity > 0 (NOT inspected before):
```
                             value  rows
                         <missing>  1608
                             check    39
                             found    28
                      OWL DOORSTOP    14
                        adjustment    14
      POLYESTER FILLER PAD 45x45cm    11
      POLYESTER FILLER PAD 40x40cm    10
                                 ?     9
                             Found     9
     FRENCH BLUE METAL DOOR SIGN 1     9
        PICNIC BASKET WICKER LARGE     8
AIRLINE BAG VINTAGE WORLD CHAMPION     8
       BOX OF 24 COCKTAIL PARASOLS     8
               MINT KITCHEN SCALES     8
   RECIPE BOX PANTRY YELLOW DESIGN     8
```

## zero_price_item (zero price, WITH customer)
```
                         value  rows
 CHRISTMAS PUDDING TRINKET POT     2
      REGENCY CAKESTAND 3 TIER     2
              6 RIBBONS EMPIRE     1
           DOOR MAT FAIRY CAKE     1
   CHRISTMAS CRAFT WHITE FAIRY     1
     ANTIQUE LILY FAIRY LIGHTS     1
ANTIQUE GLASS HEART DECORATION     1
               FLAMINGO LIGHTS     1
   CHARLOTTE BAG , SUKI DESIGN     1
     RETRO SPOT LARGE MILK JUG     1
```

## cancellation
- rows: 17,974 | with quantity > 0: 0 | with customer: 98.2%

## unclassified rows: 0
```
(none)
```

## Checks
- [PASS] overlap verified identical before dropping: 1,088 shared invoices
- [PASS] every row has exactly one type: 1,044,848 typed vs 1,044,848 rows
- [PASS] no unclassified rows: 0 found
- [PASS] no cancellation with quantity > 0: 0 found
- [PASS] shared invoices match diagnostics: 1,088 vs expected 1,088
- [PASS] rows after overlap match diagnostics: 1,044,848 vs expected 1,044,848
- [PASS] exact duplicates match diagnostics: 11,812 vs expected ~11,812