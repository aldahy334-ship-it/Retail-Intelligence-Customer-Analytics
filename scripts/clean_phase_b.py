#!/usr/bin/env python3
"""
clean_phase_b.py  -  Phase B of the cleaning plan (steps 5-10).

Reads the output of clean_phase_a.py (lines_all) and builds the analysis tables:

    sales_lines      one row per sale / cancellation line
    non_sales_lines  shipping, fees/adjustments, test/gift, stock adjustments,
                     zero-price items (kept, but outside sales analysis)
    invoices         one row per invoice
    customers        one row per Customer ID (identified customers only)
    products         one row per StockCode
    calendar         one row per day
    country_map      every country label and what it was mapped to
    sensitivity_duplicates   key figures with / without exact duplicates

Usage:
    python clean_phase_b.py --in clean_output --out clean_output/model

Nothing here deletes data: every line of lines_all lands in exactly one of
sales_lines / non_sales_lines (this is checked). Console output is plain ASCII.
Optional: put a country_overrides.csv (columns country_raw,country_clean) in
the --out folder to apply country-name fixes after we review country_map.csv.
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROW_TYPES = ["sale", "cancellation", "shipping", "fee_or_adjustment",
             "other_non_product", "stock_adjustment", "zero_price_item",
             "unclassified"]
SALES_TYPES = ["sale", "cancellation"]
GENERIC_COUNTRIES = {"Unspecified", "European Community"}   # labels, not countries
UK_NAME = "United Kingdom"

LINE_COLS = ["invoice", "stock_code", "description", "quantity", "price",
             "line_amount", "row_type", "invoice_ts", "invoice_day",
             "customer_id", "country", "is_exact_duplicate", "is_qty_outlier",
             "is_amount_outlier", "is_dotcom_code", "src_sheet", "src_row"]


# ------------------------------------------------------------------ loading
def read_lines(folder):
    pq, gz = folder / "lines_all.parquet", folder / "lines_all.csv.gz"
    if pq.exists():
        return pd.read_parquet(pq)
    if gz.exists():
        return pd.read_csv(
            gz, parse_dates=["invoice_date"],
            dtype={"invoice": "string", "stock_code": "string",
                   "description": "string", "country": "string",
                   "customer_id": "Int64", "src_sheet": "string",
                   "row_type": "string"})
    sys.exit(f"lines_all not found in {folder} (run clean_phase_a.py first)")


# ------------------------------------------------------------------- step 5
def add_derived(d):
    # الحركة 5: حسبنا مبلغ كل سطر (الكمية x السعر) مرة وحدة وخزّناه، بدل ما
    # نعيد حسابو بكل تحليل. وحطينا لكل فاتورة وقت واحد: أقدم وقت بين أسطرها
    # (لأنو في فواتير إلها وقتين بينهم دقيقة).
    d["line_amount"] = d.quantity * d.price
    d["invoice_ts"] = d.groupby("invoice")["invoice_date"].transform("min")
    d["invoice_day"] = d.invoice_ts.dt.normalize()
    # علامة لرموز DCGS: منتجات حقيقية بس بدون رقم عميل، منعلّمها بدون ما نحذفها
    d["is_dotcom_code"] = d.stock_code.str.startswith("DCGS")
    return d


# ------------------------------------------------------------------- step 9
def apply_country_map(d, out):
    # الحركة 9: ما غيّرنا أسماء الدول من راسنا. طلّعنا جدول country_map.csv
    # فيه كل اسم دولة وكم صف إلو، ونراجعو سوا. إذا بدك تصلّح اسم، حطو بملف
    # country_overrides.csv وأعد التشغيل. "Unspecified" بتضل فئة لحالها.
    d = d.rename(columns={"country": "country_raw"})
    raw = d.country_raw.astype("string").str.strip()
    ov_path = out / "country_overrides.csv"
    mapping = {}
    if ov_path.exists():
        ov = pd.read_csv(ov_path, dtype=str)
        mapping = dict(zip(ov.country_raw, ov.country_clean))
    d["country"] = raw.map(lambda x: mapping.get(x, x) if pd.notna(x) else x)
    d["country"] = d.country.fillna("Unknown")

    cm = (d.groupby("country_raw", dropna=False)
           .agg(rows=("invoice", "size"), invoices=("invoice", "nunique"),
                country_clean=("country", "first"))
           .reset_index().sort_values("rows", ascending=False))
    cm["is_generic_label"] = cm.country_clean.isin(GENERIC_COUNTRIES)
    cm.to_csv(out / "country_map.csv", index=False)
    d["is_uk"] = d.country.eq(UK_NAME)
    d["is_generic_country"] = d.country.isin(GENERIC_COUNTRIES)
    return d, cm


# ------------------------------------------------------------------- step 8
def flag_outliers(d, pct):
    # الحركة 8: ما حذفنا ولا كمية كبيرة. بس حطينا علامة على الأسطر اللي
    # كميتها أو مبلغها فوق حد (percentile) حسبناه من توزيع صفوف البيع نفسها
    # مش من راسنا. بعدين نقدر نحلل بالقيم الكبيرة وبدونها.
    sale = d[d.row_type == "sale"]
    q_thr = float(sale.quantity.quantile(pct))
    a_thr = float(sale.line_amount.quantile(pct))
    in_sales = d.row_type.isin(SALES_TYPES)
    d["is_qty_outlier"] = in_sales & (d.quantity.abs() > q_thr)
    d["is_amount_outlier"] = in_sales & (d.line_amount.abs() > a_thr)
    return d, {"pct": pct, "qty_threshold": q_thr, "amount_threshold": a_thr}


# ------------------------------------------------------------------- step 6
def split_lines(d):
    # الحركة 6أ: قسمنا الأسطر لجدولين: جدول المبيعات (بيع + إلغاء) هو اللي
    # منحلل عليه، وجدول غير المبيعات (شحن، رسوم، تسويات، بنود مجانية..)
    # منحتفظ فيه بس برّا تحليل المبيعات. مجموعهم لازم يساوي كل الأسطر.
    m = d.row_type.isin(SALES_TYPES)
    return d.loc[m, LINE_COLS], d.loc[~m, LINE_COLS]


def build_invoices(d):
    # الحركة 6ب: جدول الفواتير: صف لكل فاتورة (هون بنحسب "الطلبات").
    # نوع الفاتورة: sale إذا فيها سطر بيع، cancellation إذا فيها إلغاء بس،
    # وغير هيك non_sale (شحن/رسوم/تسويات لحالها).
    g = d.groupby("invoice")
    inv = g.agg(invoice_ts=("invoice_ts", "first"),
                customer_id=("customer_id", "first"),
                country=("country", "first"),
                n_lines=("src_row", "size"),
                n_exact_dup_lines=("is_exact_duplicate", "sum"),
                n_line_timestamps=("invoice_date", "nunique"))
    amt = (d.groupby(["invoice", "row_type"])["line_amount"].sum()
             .unstack(fill_value=0).reindex(columns=ROW_TYPES, fill_value=0))
    cnt = (d.groupby(["invoice", "row_type"]).size()
             .unstack(fill_value=0).reindex(columns=ROW_TYPES, fill_value=0))
    amt, cnt = amt.reindex(inv.index), cnt.reindex(inv.index)
    units = (d[d.row_type == "sale"].groupby("invoice")["quantity"].sum()
             .reindex(inv.index, fill_value=0))
    inv["invoice_type"] = np.select([cnt["sale"] > 0, cnt["cancellation"] > 0],
                                    ["sale", "cancellation"], "non_sale")
    inv["n_sale_lines"] = cnt["sale"]
    inv["n_cancel_lines"] = cnt["cancellation"]
    inv["units_sold"] = units
    inv["gross_sales"] = amt["sale"]
    inv["returns_amount"] = amt["cancellation"]
    inv["net_product_amount"] = amt["sale"] + amt["cancellation"]
    inv["shipping_amount"] = amt["shipping"]
    inv["fee_adjustment_amount"] = amt["fee_or_adjustment"] + amt["other_non_product"]
    inv["has_customer"] = inv.customer_id.notna()
    inv["is_uk"] = inv.country.eq(UK_NAME)
    return inv.reset_index()


def build_customers(inv):
    # الحركة 6ج: جدول العملاء: صف لكل Customer ID، من الفواتير اللي إلها
    # رقم عميل بس (الفواتير بلا رقم بتضل بالمبيعات العامة بس مش هون).
    # الدولة: دولة آخر فاتورة، لأنو في عملاء ظهروا بدولتين.
    c = inv[inv.has_customer & inv.invoice_type.isin(SALES_TYPES)].copy()
    c = c.sort_values("invoice_ts")
    g = c.groupby("customer_id")
    cust = g.agg(first_invoice_ts=("invoice_ts", "min"),
                 last_invoice_ts=("invoice_ts", "max"),
                 n_countries=("country", "nunique"),
                 country=("country", "last"),
                 units_sold=("units_sold", "sum"),
                 gross_sales=("gross_sales", "sum"),
                 returns_amount=("returns_amount", "sum"),
                 net_product_amount=("net_product_amount", "sum"))
    cust["n_orders"] = c[c.invoice_type == "sale"].groupby("customer_id").size()
    cust["n_cancel_invoices"] = (c[c.invoice_type == "cancellation"]
                                 .groupby("customer_id").size())
    cust[["n_orders", "n_cancel_invoices"]] = (
        cust[["n_orders", "n_cancel_invoices"]].fillna(0).astype(int))
    cust["has_orders"] = cust.n_orders > 0
    cust["multi_country"] = cust.n_countries > 1
    return cust.reset_index()


def build_products(sl):
    # الحركة 6د: جدول المنتجات: صف لكل رمز منتج. الوصف المعتمد هو الأكثر
    # تكرارًا بين أسطر البيع (مش أي وصف عشوائي) لأنو الرمز الواحد إلو
    # أوصاف كتيرة. بعدين نحسب لكل منتج الوحدات والمبيعات والمرتجعات.
    def best_desc(rows):
        x = rows[rows.description.notna()]
        n = (x.groupby(["stock_code", "description"]).size().reset_index(name="n")
               .sort_values(["stock_code", "n", "description"],
                            ascending=[True, False, True])
               .drop_duplicates("stock_code").set_index("stock_code")["description"])
        return n

    sale, canc = sl[sl.row_type == "sale"], sl[sl.row_type == "cancellation"]
    desc = best_desc(sale)
    fallback = best_desc(canc)
    gs = sale.groupby("stock_code")
    prod = pd.DataFrame({
        "units_sold": gs["quantity"].sum(),
        "gross_sales": gs["line_amount"].sum(),
        "n_orders": gs["invoice"].nunique(),
        "n_customers": gs["customer_id"].nunique(),
        "first_sale_ts": gs["invoice_ts"].min(),
        "last_sale_ts": gs["invoice_ts"].max(),
        "min_unit_price": gs["price"].min(),
        "max_unit_price": gs["price"].max()})
    gc = canc.groupby("stock_code")
    prod = prod.join(pd.DataFrame({"units_returned": -gc["quantity"].sum(),
                                   "returns_amount": gc["line_amount"].sum()}),
                     how="outer")
    for col in ("units_sold", "gross_sales", "n_orders", "n_customers",
                "units_returned", "returns_amount"):
        prod[col] = prod[col].fillna(0)
    prod["avg_unit_price"] = (prod.gross_sales / prod.units_sold.replace(0, np.nan))
    prod["product_description"] = desc.reindex(prod.index)
    prod["product_description"] = prod.product_description.fillna(
        fallback.reindex(prod.index))
    prod["n_descriptions_seen"] = (sl[sl.description.notna()]
                                   .groupby("stock_code")["description"].nunique()
                                   .reindex(prod.index).fillna(0).astype(int))
    prod["is_dotcom_code"] = prod.index.str.startswith("DCGS")
    prod["net_product_amount"] = prod.gross_sales + prod.returns_amount
    return prod.reset_index().rename(columns={"index": "stock_code"})


# ------------------------------------------------------------------ step 10
def build_calendar(inv):
    # الحركة 10: جدول تقويم: صف لكل يوم بين أول وآخر فاتورة، مع السنة والشهر
    # واليوم. وعلّمنا الأشهر الناقصة (متل ديسمبر 2011 اللي بينتهي بـ 9 منو)
    # عشان ما نقارن شهر ناقص بشهر كامل بالغلط.
    lo, hi = inv.invoice_ts.min(), inv.invoice_ts.max()
    days = pd.date_range(lo.normalize(), hi.normalize(), freq="D")
    cal = pd.DataFrame({"date": days})
    cal["year"] = cal.date.dt.year
    cal["month"] = cal.date.dt.month
    cal["month_name"] = cal.date.dt.month_name()
    cal["year_month"] = cal.date.dt.strftime("%Y-%m")
    cal["quarter"] = cal.date.dt.quarter
    cal["weekday_num"] = cal.date.dt.dayofweek + 1        # Mon = 1
    cal["weekday_name"] = cal.date.dt.day_name()
    partial = set()
    if lo.day > 1:
        partial.add(lo.strftime("%Y-%m"))
    if hi.normalize() < (hi + pd.offsets.MonthEnd(0)).normalize():
        partial.add(hi.strftime("%Y-%m"))
    cal["is_partial_month"] = cal.year_month.isin(partial)
    return cal, sorted(partial)


# ----------------------------------------------------------- sensitivity
def kpis(sl):
    sale = sl[sl.row_type == "sale"]
    canc = sl[sl.row_type == "cancellation"]
    gross, ret = sale.line_amount.sum(), canc.line_amount.sum()
    orders = sale.invoice.nunique()
    return {"sale_lines": len(sale), "orders": orders,
            "customers": sale.customer_id.nunique(),
            "units_sold": sale.quantity.sum(), "gross_sales": gross,
            "returns": ret, "net_product_revenue": gross + ret,
            "avg_order_value": gross / orders if orders else np.nan}


def sensitivity(sl):
    # الحركة 7: sensitivity analysis: حسبنا الأرقام الرئيسية مرتين، مع
    # المكرر وبدونو، وقارنّا الفرق. هيك منعرف إذا قرار "نبقي المكرر" بيغيّر
    # النتيجة ولا لأ.
    a = kpis(sl)
    b = kpis(sl[~sl.is_exact_duplicate])
    t = pd.DataFrame({"with_duplicates": a, "without_duplicates": b})
    t["difference"] = t.with_duplicates - t.without_duplicates
    t["difference_pct"] = 100 * t.difference / t.with_duplicates
    return t.round(2)


# -------------------------------------------------------------------- checks
def run_checks(d, sl, nsl, inv, cust, prod, cal):
    sale_amt = sl.loc[sl.row_type == "sale", "line_amount"].sum()
    net_all = sl.line_amount.sum()
    cust_net = cust.net_product_amount.sum()
    nocust_net = inv.loc[~inv.has_customer & inv.invoice_type.isin(SALES_TYPES),
                         "net_product_amount"].sum()
    multi = (d.groupby("invoice")
              .agg(c=("customer_id", "nunique"), k=("country", "nunique")))
    ok = lambda a, b: bool(np.isclose(a, b, rtol=0, atol=0.01))
    return [
        ("every line in exactly one table (sales + non-sales = all)",
         len(sl) + len(nsl) == len(d), f"{len(sl):,} + {len(nsl):,} vs {len(d):,}"),
        ("invoices: one row per invoice", inv.invoice.is_unique,
         f"{len(inv):,} rows"),
        ("products: one row per stock code", prod.stock_code.is_unique,
         f"{len(prod):,} rows"),
        ("customers: one row per customer", cust.customer_id.is_unique,
         f"{len(cust):,} rows"),
        ("no invoice with >1 customer or >1 country",
         int((multi.c > 1).sum() + (multi.k > 1).sum()) == 0,
         f"{int((multi.c > 1).sum())} customer / {int((multi.k > 1).sum())} country"),
        ("invoice gross sales = line gross sales",
         ok(inv.gross_sales.sum(), sale_amt), f"{inv.gross_sales.sum():,.2f}"),
        ("product gross sales = line gross sales",
         ok(prod.gross_sales.sum(), sale_amt), f"{prod.gross_sales.sum():,.2f}"),
        ("customer net + no-customer net = total net",
         ok(cust_net + nocust_net, net_all),
         f"{cust_net + nocust_net:,.2f} vs {net_all:,.2f}"),
        ("calendar covers every invoice day",
         bool(inv.invoice_ts.dt.normalize().isin(cal.date).all()), ""),
        ("sale lines all have quantity > 0 and price > 0",
         bool(((sl[sl.row_type == "sale"].quantity > 0)
               & (sl[sl.row_type == "sale"].price > 0)).all()), ""),
    ]


# ----------------------------------------------------------------- reporting
def build_report(d, sl, nsl, inv, cust, prod, cal, partial, outl, sens, cm,
                 checks, runtime):
    L, w = [], None
    L = []
    w = L.append

    def T(df):
        w("```")
        w(df.to_string(index=False, max_colwidth=40) if len(df) else "(none)")
        w("```")

    w("# Phase B report (steps 5-10)")
    w(f"runtime {runtime:.0f}s | lines_all rows: {len(d):,}")
    w("")
    w("## Tables built")
    T(pd.DataFrame({
        "table": ["sales_lines", "non_sales_lines", "invoices", "customers",
                  "products", "calendar"],
        "rows": [len(sl), len(nsl), len(inv), len(cust), len(prod), len(cal)]}))
    w("")
    w("## non_sales_lines by type")
    T(nsl.row_type.value_counts().rename_axis("row_type").reset_index(name="rows"))
    w("")
    w("## invoices by type")
    T(inv.invoice_type.value_counts().rename_axis("invoice_type").reset_index(name="invoices"))
    w(f"- invoices without Customer ID: {int((~inv.has_customer).sum()):,} "
      f"({(~inv.has_customer).mean():.1%})")
    w(f"- invoices whose lines had >1 timestamp (earliest used): "
      f"{int((inv.n_line_timestamps > 1).sum()):,}")
    w("")
    w("## Sensitivity: exact duplicates kept vs removed (product-only figures)")
    T(sens.reset_index().rename(columns={"index": "metric"}))
    w("")
    w("## Outlier flags (flag only, nothing removed)")
    w(f"- rule: abs(quantity) or abs(line amount) above the {outl['pct']:.3%} "
      f"percentile of SALE lines")
    w(f"- quantity threshold: {outl['qty_threshold']:,.0f} | amount threshold: "
      f"{outl['amount_threshold']:,.2f}")
    w(f"- flagged lines: quantity={int(sl.is_qty_outlier.sum()):,}, "
      f"amount={int(sl.is_amount_outlier.sum()):,}")
    w("- 10 largest sale lines by quantity:")
    T(sl[sl.row_type == "sale"].nlargest(10, "quantity")
      [["invoice", "stock_code", "description", "quantity", "price", "customer_id"]])
    w("")
    w("## Customers")
    w(f"- customers: {len(cust):,} | with at least one order: "
      f"{int(cust.has_orders.sum()):,} | with >1 country: "
      f"{int(cust.multi_country.sum())}")
    w("")
    w("## Calendar")
    w(f"- range: {cal.date.min().date()} to {cal.date.max().date()} | "
      f"partial months: {partial}")
    wd = (inv.invoice_ts.dt.day_name().value_counts()
             .rename_axis("weekday").reset_index(name="invoices"))
    T(wd)
    w("")
    w("## Country map (full list - please review)")
    T(cm[["country_raw", "rows", "invoices", "country_clean", "is_generic_label"]])
    w("")
    w("## Checks")
    for name, ok, detail in checks:
        w(f"- [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    return "\n".join(L)


# ----------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", default="clean_output")
    ap.add_argument("--out", default="clean_output/model")
    ap.add_argument("--outlier-pct", type=float, default=0.999)
    a = ap.parse_args()
    inp, out = Path(a.inp), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    d = read_lines(inp)
    d = add_derived(d)
    d, cm = apply_country_map(d, out)
    d, outl = flag_outliers(d, a.outlier_pct)
    sl, nsl = split_lines(d)
    inv = build_invoices(d)
    cust = build_customers(inv)
    prod = build_products(sl)
    cal, partial = build_calendar(inv)
    sens = sensitivity(sl)
    checks = run_checks(d, sl, nsl, inv, cust, prod, cal)

    # حفظنا كل جدول بملف CSV (Power BI بيقراهم مباشرة)
    for name, df in [("sales_lines", sl), ("non_sales_lines", nsl),
                     ("invoices", inv), ("customers", cust),
                     ("products", prod), ("calendar", cal)]:
        df.to_csv(out / f"{name}.csv", index=False)
    sens.reset_index().rename(columns={"index": "metric"}).to_csv(
        out / "sensitivity_duplicates.csv", index=False)

    rep = build_report(d, sl, nsl, inv, cust, prod, cal, partial, outl, sens,
                       cm, checks, time.time() - t0)
    (out / "phase_b_report.md").write_text(rep, encoding="utf-8")

    print("\nTables:")
    for n, df in [("sales_lines", sl), ("non_sales_lines", nsl), ("invoices", inv),
                  ("customers", cust), ("products", prod), ("calendar", cal)]:
        print(f"  {n:16s} {len(df):>10,} rows")
    print("\nChecks:")
    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    print(f"\nReport: {out / 'phase_b_report.md'}  (share this one)")


if __name__ == "__main__":
    main()
