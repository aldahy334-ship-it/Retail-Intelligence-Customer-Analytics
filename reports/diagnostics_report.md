# Retail diagnostics (online_retail_II.xlsx)
rows loaded: 1,067,371 | sheets: ['Year 2009-2010', 'Year 2010-2011']

## 1. Shared invoices across sheets
- sheets: A=`Year 2009-2010`, B=`Year 2010-2011`
- invoices: A=28,816 B=25,900 shared=1,088
- rows inside shared invoices: A=22,523 B=22,523
- date span of shared-invoice rows: 2010-12-01 08:26:00 -> 2010-12-09 20:01:00
- line-set comparison (full-row multiset, duplicates counted):
```
   status  invoices
identical      1088
```
- lines only in A: 0 | only in B: 0
- invoice-level header mismatches between sheets: earliest timestamp=0, latest timestamp=0, customer=0, country=0
- overlap window by date: 2010-12-01 08:26:00 -> 2010-12-09 20:01:00
- sheet A rows in window: 22,523 (distinct full rows 22,202); invoice also in other sheet: 22,523; invoice NOT in other sheet: 0 (0 invoices)
- sheet B rows in window: 22,523 (distinct full rows 22,202); invoice also in other sheet: 22,523; invoice NOT in other sheet: 0 (0 invoices)

## 2. Non-product / rare-shape stock codes
- dominant code shapes (>=1% of all rows; 9=digit, A=letter): `['99999', '99999A']`
- rows with a non-dominant shape: 7,465 across 67 distinct raw codes
- ALL non-dominant-shape codes (sheets: 0=A only, 1=B only, 01=both):
```
         stk  rows  invoices  n_desc  qty_sum    val_sum  price_min  price_med  price_max  pct_cust  pct_C sheets                     top_description
        POST  2122      2084       1    10108  112341.00       0.00      18.00    8142.75      95.0   11.0     01                             POSTAGE
         DOT  1446      1425       1     2938  322647.47       0.00     154.18    4505.17       1.0    0.0     01                      DOTCOM POSTAGE
           M  1421      1286       1     4607  -82796.32       0.00      12.68   38970.00      78.0   38.0     01                              Manual
     15056BL   923       870       1     9523   47030.54       0.00       5.95      13.00      92.0    1.0     01             EDWARDIAN PARASOL BLACK
          C2   282       277       1      716   13386.00       0.00      50.00     150.00      92.0    2.0     01                            CARRIAGE
     79323LP   232       231       2    -1651    5778.39       0.00       6.75      13.87      94.0   26.0     01            LIGHT PINK CHERRY LIGHTS
           D   177       151       1    -2872  -13484.54       0.01      19.00    1867.86      98.0   97.0     01                            Discount
     79323GR   123       123       3    -2014    2040.86       0.00       6.75      13.87      92.0   30.0     01                 GREEN CHERRY LIGHTS
           S   104        37       1      -98   -6065.80       2.80      29.99     605.18       0.0   97.0     01                             SAMPLES
BANK CHARGES   102        95       2      -42  -35562.63       0.00      42.12   18910.69      37.0   66.0     01                        Bank Charges
     15056bl    93        87       1      126    1583.52      12.46      12.46      13.00       0.0    0.0     01             EDWARDIAN PARASOL BLACK
      ADJUST    67        67       3        5    6835.24       4.57      49.35    5117.03      91.0   46.0      0 Adjustment by john on 26/01/2010 16
   AMAZONFEE    43        36       1      -35 -260763.58       1.00    6497.47   17836.46       0.0   91.0     01                          AMAZON FEE
    DCGS0058    31        31       1       43      34.82       0.00       0.83       0.95       0.0    0.0      0                    MISO PRETTY  GUM
gift_0001_20    29        29       2       53     471.06       0.00      17.02      17.39       0.0    0.0     01  Dotcomgiftshop Gift Voucher £20.00
gift_0001_30    29        29       1       77     610.09       0.00      25.53      26.08       0.0    0.0     01  Dotcomgiftshop Gift Voucher £30.00
   DCGSSGIRL    25        25       2      191     295.63       0.00       3.29       3.36       0.0    0.0     01                     GIRLS PARTY BAG
    DCGSSBOY    23        23       2       87     251.35       0.00       3.29       3.36       0.0    0.0     01                      BOYS PARTY BAG
        PADS    19        19       1       17     -36.58       0.00       0.00      36.60     100.0    5.0     01          PADS TO MATCH ALL CUSHIONS
gift_0001_10    16        16       1       55     126.21       0.00       8.33       8.69       0.0    0.0     01  Dotcomgiftshop Gift Voucher £10.00
        CRUK    16        16       1      -16   -7933.43       1.60     471.77    1100.44     100.0  100.0      1                     CRUK Commission
     TEST001    15        15       1       55     202.50       0.00       4.50       4.50     100.0   27.0      0             This is a test product.
    DCGS0076    15        14       1       18     292.09      16.13      16.13      16.48       0.0    0.0     01        SUNJAR LED NIGHT NIGHT LIGHT
    DCGS0003    14        14       2        6      32.59       0.00       2.51       2.57       0.0    0.0     01                 BOXED GLASS ASHTRAY
gift_0001_50     8         8       1       19     253.59       0.00      41.67      43.48       0.0    0.0     01  Dotcomgiftshop Gift Voucher £50.00
gift_0001_40     7         7       1       18     166.09       0.00      33.33      34.04       0.0    0.0     01  Dotcomgiftshop Gift Voucher £40.00
           B     6         6       1        6 -147614.08  -53594.36  -24993.96   11062.06       0.0    0.0     01                     Adjust bad debt
    DCGS0069     6         6       2        0      80.31       0.00      16.13      16.13       0.0    0.0     01               OOH LA LA DOGS COLLAR
           m     5         4       1        5      15.05       2.55       2.55       4.00       0.0    0.0     01                              Manual
    DCGS0004     5         5       1        2      67.94       0.00      16.98      17.35       0.0    0.0     01          HAYNES CAMPER SHOULDER BAG
   DCGS0066N     4         4       1        4      17.30       0.00       4.32       8.65       0.0    0.0      0                           <missing>
    DCGS0072     4         4       1        3      20.68       0.00       5.17       5.17       0.0    0.0     01              CAT CAMOUFLAGUE COLLAR
gift_0001_80     4         4       1       12       0.00       0.00      34.78      69.56       0.0   25.0      0                           <missing>
gift_0001_70     3         3       1       13      59.57       0.00       0.00      59.57       0.0    0.0      0                           <missing>
     ADJUST2     3         3       1        3     731.05      72.45     300.13     358.47     100.0    0.0      0  Adjustment by Peter on Jun 25 2010
    DCGS0070     3         3       1       -6      25.44       0.00      12.72      12.72       0.0    0.0     01               CAMOUFLAGE DOG COLLAR
    DCGS0068     3         3       2       -8      17.12       0.00       8.47       8.65       0.0    0.0     01                   DOGS NIGHT COLLAR
      SP1002     3         3       1      -22      14.75       0.00       2.95       2.95      67.0    0.0      0              KID'S CHALKBOARD/EASEL
gift_0001_90     2         2       0       12       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
    DCGS0037     2         2       1        0      12.72       0.00       6.36      12.72       0.0    0.0      0                           <missing>
    DCGS0062     2         2       1        0       2.51       0.00       1.25       2.51       0.0    0.0      0                           <missing>
gift_0001_60     2         2       0       13       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
     TEST002     2         2       1        2       1.00       0.00       0.50       1.00      50.0    0.0      0                           <missing>
     72024HC     1         1       0    -3669       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
    DCGS0039     1         1       0       -1       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
    DCGS0036     1         1       0       -1       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
    DCGS0044     1         1       1        1       2.57       2.57       2.57       2.57       0.0    0.0      0             HANDZ-OFF CAR FRESHENER
          C3     1         1       0    -4999       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
    DCGS0006     1         1       0       -1       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
    DCGS0016     1         1       0       -1       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
    DCGS0027     1         1       0       -1       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
    DCGS0067     1         1       1      -11       0.00       0.00       0.00       0.00       0.0    0.0      1                                ebay
   DCGS0066P     1         1       0       -3       0.00       0.00       0.00       0.00       0.0    0.0      1                           <missing>
    DCGS0059     1         1       0       -8       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
    DCGS0060     1         1       0       -3       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
    DCGS0057     1         1       0       -6       0.00       0.00       0.00       0.00       0.0    0.0      1                           <missing>
    DCGS0053     1         1       0       -2       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
    DCGS0055     1         1       0       -1       0.00       0.00       0.00       0.00       0.0    0.0      1                           <missing>
    DCGS0056     1         1       0       -4       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
    DCGS0041     1         1       1        1       5.06       5.06       5.06       5.06       0.0    0.0      0    HAYNES MINI-COOPER PLAYING CARDS
        GIFT     1         1       0       -9       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
    DCGSLBOY     1         1       0      -16       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
   DCGSLGIRL     1         1       0      -57       0.00       0.00       0.00       0.00       0.0    0.0      0                           <missing>
    DCGS0071     1         1       0       -2       0.00       0.00       0.00       0.00       0.0    0.0      1                           <missing>
    DCGS0073     1         1       1       -4       0.00       0.00       0.00       0.00       0.0    0.0      1                                ebay
    DCGS0074     1         1       0       -1       0.00       0.00       0.00       0.00       0.0    0.0      1                           <missing>
    DCGS0075     1         1       1        1      12.72      12.72      12.72      12.72       0.0    0.0      0                CAMOUFLAGUE DOG LEAD
```
- NOTE: shape alone is not a product test; some codes here may be real products (decide from description, price and customer columns).
- dominant-shape codes with >=10 rows where >=50% are zero-price or description-missing: 0
```
(none)
```

## 3. Negative prices and A-prefixed invoices
- negative-price rows: 5
```
 _sheet     inv StockCode     Description  Quantity     Price  Customer ID        Country         InvoiceDate
      0 A506401         B Adjust bad debt         1 -53594.36          NaN United Kingdom 2010-04-29 13:36:00
      0 A516228         B Adjust bad debt         1 -44031.79          NaN United Kingdom 2010-07-19 11:24:00
      0 A528059         B Adjust bad debt         1 -38925.87          NaN United Kingdom 2010-10-20 12:04:00
      1 A563186         B Adjust bad debt         1 -11062.06          NaN United Kingdom 2011-08-12 14:51:00
      1 A563187         B Adjust bad debt         1 -11062.06          NaN United Kingdom 2011-08-12 14:52:00
```
- rows on invoices with a non-C letter prefix: 6 (6 invoices; prefixes ['A'])
```
 _sheet     inv StockCode     Description  Quantity     Price  Customer ID        Country         InvoiceDate
      0 A506401         B Adjust bad debt         1 -53594.36          NaN United Kingdom 2010-04-29 13:36:00
      0 A516228         B Adjust bad debt         1 -44031.79          NaN United Kingdom 2010-07-19 11:24:00
      0 A528059         B Adjust bad debt         1 -38925.87          NaN United Kingdom 2010-10-20 12:04:00
      1 A563185         B Adjust bad debt         1  11062.06          NaN United Kingdom 2011-08-12 14:50:00
      1 A563186         B Adjust bad debt         1 -11062.06          NaN United Kingdom 2011-08-12 14:51:00
      1 A563187         B Adjust bad debt         1 -11062.06          NaN United Kingdom 2011-08-12 14:52:00
```
- invoices that are BOTH negative-price and non-C-prefixed: 5
- total lines on those prefixed invoices: 6 (extra lines beyond the prefixed rows: 0)

## 4. Non-C negative quantities: is Price always 0?
- non-C rows with Quantity < 0: 3,457
```
 _sheet  zero
      0  2121
      1  1336
```
- with a Customer ID: 0
- non-C negative rows with Price > 0: 0
```
(none)
```
- reverse check: C-prefix rows with Price == 0: 0; C-prefix rows with Quantity > 0: 1
```
 _sheet     inv StockCode Description  Quantity  Price  Customer ID         InvoiceDate
      0 C496350         M      Manual         1 373.57          NaN 2010-02-01 08:24:00
```
- top descriptions on non-C negative rows:
```
           description  rows
             <missing>  2689
                 check   123
               damages    84
                     ?    83
               damaged    78
               missing    27
 sold as set on dotcom    20
               Damaged    17
               smashed     9
           thrown away     9
Unsaleable, destroyed.     9
                dotcom     8
              damages?     7
                    ??     7
               crushed     6
```

## 5. Zero-price rows that still have a Customer ID
- zero-price rows: 6,202 | with customer: 71 | without: 6,131
- with customer, by sheet / sign of quantity / C-prefix / non-dominant code:
```
 sheet  qty_sign  is_C  nonstd_code  rows
     1         1 False        False    33
     0         1 False        False    28
     1         1 False         True     7
     0         1 False         True     3
```
- description missing: with-customer=0.0% vs without-customer=71.5%
- distinct customers: 51 (top by rows below)
```
 customer  rows
  12647.0     6
  14646.0     5
  13081.0     4
  13047.0     3
  14108.0     2
  12748.0     2
  17667.0     2
  14911.0     2
  12415.0     2
  13985.0     2
```
- invoices containing them: 61
```
                              invoice_kind  invoices
zero-price lines on an otherwise priced...        55
                      all lines zero-price         6
```
- top descriptions (with customer):
```
                      description  rows
                           Manual     7
    CHRISTMAS PUDDING TRINKET POT     2
          This is a test product.     2
         REGENCY CAKESTAND 3 TIER     2
     ROUND CAKE TIN VINTAGE GREEN     2
                 6 RIBBONS EMPIRE     1
              DOOR MAT FAIRY CAKE     1
      CHRISTMAS CRAFT WHITE FAIRY     1
        ANTIQUE LILY FAIRY LIGHTS     1
   ANTIQUE GLASS HEART DECORATION     1
                  FLAMINGO LIGHTS     1
      CHARLOTTE BAG , SUKI DESIGN     1
        RETRO SPOT LARGE MILK JUG     1
       VINTAGE GLASS COFFEE CADDY     1
     CAST IRON HOOK GARDEN TROWEL     1
       CAST IRON HOOK GARDEN FORK     1
AIRLINE BAG VINTAGE JET SET WHITE     1
          HANGING METAL BIRD BATH     1
 SET/5 RED SPOTTY LID GLASS BOWLS     1
     DOORMAT HOME SWEET HOME BLUE     1
```
- sample rows:
```
 _sheet    inv StockCode                      Description  Quantity  Price  Customer ID        Country         InvoiceDate
      0 531361     21843         RED RETROSPOT CAKE STAND         2    0.0      12820.0 United Kingdom 2010-11-07 14:26:00
      0 532470     22624             IVORY KITCHEN SCALES         2    0.0      12647.0        Germany 2010-11-12 11:41:00
      1 564651     23270 SET OF 2 CERAMIC PAINTED HEARTS         96    0.0      14646.0    Netherlands 2011-08-26 14:19:00
      0 524181    46000M     POLYESTER FILLER PAD 45x45cm       648    0.0      17450.0 United Kingdom 2010-09-27 16:59:00
      0 537197     22841     ROUND CAKE TIN VINTAGE GREEN         1    0.0      12647.0        Germany 2010-12-05 14:02:00
      1 564651     21786               POLKADOT RAIN HAT        144    0.0      14646.0    Netherlands 2011-08-26 14:19:00
      0 493761     79320                  FLAMINGO LIGHTS        24    0.0      14258.0 United Kingdom 2010-01-06 14:54:00
      1 574252         M                           Manual         1    0.0      12437.0         France 2011-11-03 13:24:00
      1 540372     22090          PAPER BUNTING RETROSPOT        24    0.0      13081.0 United Kingdom 2011-01-06 16:41:00
      1 578841     84826   ASSTD DESIGN 3D PAPER STICKERS     12540    0.0      13256.0 United Kingdom 2011-11-25 15:57:00
      1 572893     21208      PASTEL COLOUR HONEYCOMB FAN         5    0.0      18059.0 United Kingdom 2011-10-26 14:36:00
      0 533822     22846       BREAD BIN DINER STYLE RED          1    0.0      12647.0        Germany 2010-11-19 09:40:00
      1 537197     22841     ROUND CAKE TIN VINTAGE GREEN         1    0.0      12647.0        Germany 2010-12-05 14:02:00
      1 553000     47566                    PARTY BUNTING         4    0.0      17667.0 United Kingdom 2011-05-12 15:21:00
      1 539722     22423         REGENCY CAKESTAND 3 TIER        10    0.0      14911.0           EIRE 2010-12-21 13:45:00
```

## 6. Exact duplicate rows within sheets
- extra (removable) rows: 12,133 (by sheet: {0: 6865, 1: 5268}); duplicated groups: 11,297
- group size distribution (rows per identical group):
```
 group_size(5=5+)  groups
                2   10625
                3     568
                4      79
                5      25
```
- invoices with >=1 duplicate: 4,471 of 54,716 (8.2%)
- invoices where EVERY line is duplicated: 10
```
extra_rows/lines  invoices
     (0.0, 0.05]      2577
     (0.05, 0.1]      1311
     (0.1, 0.25]       557
     (0.25, 0.5]        25
      (0.5, 1.0]         1
```
- concentration: top 10 invoices hold 2.4% of extra rows; top 10% of affected invoices hold 35.6%
```
 _sheet    inv  lines  min_g               dates  has_cust  is_c  extra
      1 555524     76      1 2011-06-05 11:37:00      True False     34
      0 530437    146      1 2010-11-03 11:13:00      True False     33
      1 547651    114      1 2011-03-24 12:11:00      True False     31
      0 525075    132      1 2010-10-03 15:24:00      True False     31
      1 579458    126      1 2011-11-29 14:38:00      True False     28
      1 574481    191      1 2011-11-04 12:45:00      True False     27
      1 572103    223      1 2011-10-20 15:57:00      True False     27
      1 577482     55      1 2011-11-20 11:43:00      True False     26
      0 531922    178      1 2010-11-10 12:09:00      True False     26
      0 537781    161      1 2010-12-08 12:46:00      True False     25
```
- adjacency of repeated rows in file order: gap==1 14.0%, <=5 38.3%, <=50 93.4%, median gap 9
- profile: duplicate-extra rows vs all rows (share):
```
           metric  extra_rows  all_rows
         C-prefix      0.0050    0.0183
   no Customer ID      0.0113    0.2277
       Price == 0      0.0009    0.0058
non-dominant code      0.0030    0.0070
    Quantity == 1      0.7066    0.2758
     Quantity < 0      0.0050    0.0215
```
- duplicate-extra rate by sheet/month (extra rows / rows):
```
 _sheet   month   rate
      0 2009-12 0.0112
      0 2010-01 0.0102
      0 2010-02 0.0112
      0 2010-03 0.0127
      0 2010-04 0.0120
      0 2010-05 0.0117
      0 2010-06 0.0129
      0 2010-07 0.0117
      0 2010-08 0.0110
      0 2010-09 0.0115
      0 2010-10 0.0144
      0 2010-11 0.0183
      0 2010-12 0.0143
      1 2010-12 0.0118
      1 2011-01 0.0070
      1 2011-02 0.0082
      1 2011-03 0.0084
      1 2011-04 0.0072
      1 2011-05 0.0067
      1 2011-06 0.0072
      1 2011-07 0.0064
      1 2011-08 0.0062
      1 2011-09 0.0073
      1 2011-10 0.0127
      1 2011-11 0.0161
      1 2011-12 0.0109
```
- value impact (Quantity*Price) of extra rows: net=55,450.05; on normal sale rows=58,703.10 = 0.28% of normal-sale value (pre-overlap-resolution, descriptive only)
- repeated (sheet,invoice,stock) groups: 21,758; all-identical: 10,335; contain different lines: 11,423
```
                 how_lines_differ  groups
                      qty differs   10461
                 qty+price differ     761
                    price differs     197
other (desc/date/customer differ)       4
```
- extra rows inside the shared (cross-sheet) invoices: 642
- shared-invoice lines duplicated in at least one sheet: 296; same multiplicity in both sheets: 296 (100.0%)

_runtime 126s | source file unchanged: **True**_