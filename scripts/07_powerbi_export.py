#!/usr/bin/env python3
"""
07_powerbi_export.py  -  Step 8a: Export a clean star-schema dataset for the Power BI dashboard

Reads : <in>/invoices.csv, calendar.csv, products.csv                 (default: clean_output/model)
        <out>/02_product_ranking.csv, 04_customer_rfm.csv, 04_segment_summary.csv,
        <out>/05_cohort_retention.csv, 05_cohort_summary.csv           (default: analysis_output)
Writes: <out>/powerbi/fact_invoices.csv          one row per invoice (53,628)
        <out>/powerbi/fact_cohort_retention.csv  cohort x months-since-first (long format)
        <out>/powerbi/dim_calendar.csv, dim_country.csv, dim_customer.csv, dim_product.csv
        <out>/07_powerbi_export_report.md

Analytical decisions (see cleaning_log.md):
  * RFM, segments and cohorts are NOT recomputed here. They are read from steps 5 and 6, so the
    dashboard shows exactly the numbers of the reports. Power BI (DAX) only does simple sums/ratios.
  * fact_invoices keeps the D13 invoices and flags them (is_d13 = 1). DAX measures for Gross and
    Returns exclude them (D13); Net revenue includes them because the pairs net to zero.
  * Partial month (2011-12) is flagged in dim_calendar (is_partial_month) so visuals can exclude it.
  * Customers without a Customer ID stay in fact_invoices (customer_id blank, has_customer = 0).
  * Products: the D13 codes and dotcom codes are flagged, not removed.
  * Read-only on all source files: only the powerbi/ subfolder and the report are written.

Usage:  python 07_powerbi_export.py [--in clean_output/model] [--out analysis_output]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

UK = "United Kingdom"
D13_INVOICES = ["581483", "C581484", "541431", "C541433"]
D13_CODES = ["23843", "23166"]
FAMILY = "79323"
GENERIC_COUNTRIES = ["Unspecified", "European Community"]
SEGMENT_ORDER = ["Champions", "Loyal", "New / Promising", "Needs Attention", "At Risk", "Hibernating"]

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="indir", default="clean_output/model")
ap.add_argument("--out", default="analysis_output")
args = ap.parse_args()
IN, OUT = Path(args.indir), Path(args.out)
PBI = OUT / "powerbi"

need = [IN / "invoices.csv", IN / "calendar.csv", IN / "products.csv",
        OUT / "02_product_ranking.csv", OUT / "04_customer_rfm.csv", OUT / "04_segment_summary.csv",
        OUT / "05_cohort_retention.csv", OUT / "05_cohort_summary.csv"]
missing = [str(p) for p in need if not p.exists()]
if missing:
    sys.exit("Missing input files (run the earlier steps first):\n  " + "\n  ".join(missing))
PBI.mkdir(parents=True, exist_ok=True)


def md(df):
    """Minimal Markdown table (no tabulate dependency)."""
    cols = [str(c) for c in df.columns]
    rows = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    rows += ["| " + " | ".join(map(str, r)) + " |" for r in df.itertuples(index=False)]
    return "\n".join(rows)


written = []


def save(df, name):
    """UTF-8 with BOM so Power BI reads text correctly; dates are plain YYYY-MM-DD strings."""
    df.to_csv(PBI / name, index=False, encoding="utf-8-sig")
    written.append({"file": name, "rows": len(df), "columns": ", ".join(df.columns)})


def to_date(s):
    return pd.to_datetime(s).dt.strftime("%Y-%m-%d")


def flag(s):
    return s.astype(str).str.lower().eq("true").astype(int)


# ------------------------------------------------------------------ 1. fact_invoices
inv = pd.read_csv(IN / "invoices.csv", dtype={"invoice": str}, low_memory=False)
inv["invoice_ts"] = pd.to_datetime(inv["invoice_ts"])
inv["customer_id"] = pd.to_numeric(inv["customer_id"], errors="coerce").astype("Int64")
money = ["gross_sales", "returns_amount", "net_product_amount", "shipping_amount", "fee_adjustment_amount"]
fi = pd.DataFrame({
    "invoice": inv["invoice"],
    "invoice_date": inv["invoice_ts"].dt.normalize().dt.strftime("%Y-%m-%d"),
    "invoice_month": inv["invoice_ts"].dt.to_period("M").dt.to_timestamp().dt.strftime("%Y-%m-%d"),
    "customer_id": inv["customer_id"],
    "country": inv["country"],
    "n_lines": inv["n_lines"],
    "units_sold": inv["units_sold"],
})
for col in money:
    fi[col] = inv[col].round(4)          # 4 decimals: sums match the reports (2 decimals would drift by ~0.02)
fi["is_order"] = (inv["n_sale_lines"] > 0).astype(int)              # order = invoice with >= 1 sale line
fi["is_cancel_invoice"] = (inv["n_cancel_lines"] > 0).astype(int)
fi["is_d13"] = inv["invoice"].isin(D13_INVOICES).astype(int)
fi["has_customer"] = inv["customer_id"].notna().astype(int)
save(fi, "fact_invoices.csv")

# ------------------------------------------------------------------ 2. dim_calendar, dim_country
cal = pd.read_csv(IN / "calendar.csv")
cal["is_partial_month"] = flag(cal["is_partial_month"])
cal["date"] = to_date(cal["date"])
cal = cal.sort_values("date")
cal["month_start"] = cal["date"].str[:7] + "-01"
save(cal, "dim_calendar.csv")

dc = pd.DataFrame({"country": sorted(inv["country"].dropna().unique())})
dc["market"] = np.where(dc["country"] == UK, "UK", "International")
dc["is_generic_label"] = dc["country"].isin(GENERIC_COUNTRIES).astype(int)   # not real countries
save(dc, "dim_country.csv")

# ------------------------------------------------------------------ 3. dim_customer (from step 5)
rfm = pd.read_csv(OUT / "04_customer_rfm.csv", dtype={"rfm_code": str}, low_memory=False)
seg_file = pd.read_csv(OUT / "04_segment_summary.csv")
rfm["first_order_date"] = to_date(rfm["first_order_ts"])
rfm["last_order_date"] = to_date(rfm["last_order_ts"])
rfm["segment_sort"] = rfm["segment"].map({s: i + 1 for i, s in enumerate(SEGMENT_ORDER)})
dcu = rfm[["customer_id", "country", "orders", "first_order_date", "last_order_date", "recency_days",
           "gross_sales", "returns_amount", "net_revenue", "n_cancel_invoices", "R", "F", "M",
           "rfm_code", "segment", "segment_sort"]]
save(dcu, "dim_customer.csv")

# ------------------------------------------------------------------ 4. dim_product (+ rank from step 3)
p = pd.read_csv(IN / "products.csv", dtype={"stock_code": str}, low_memory=False)
rk = pd.read_csv(OUT / "02_product_ranking.csv", dtype={"stock_code": str}, low_memory=False)
rk["product_rank"] = np.arange(1, len(rk) + 1)                       # file is sorted by net revenue
p["is_dotcom_code"] = flag(p["is_dotcom_code"])
p["is_d13_code"] = p["stock_code"].isin(D13_CODES).astype(int)
p["is_family_79323"] = p["stock_code"].str.startswith(FAMILY).astype(int)
p["first_sale_date"] = to_date(p["first_sale_ts"])
p["last_sale_date"] = to_date(p["last_sale_ts"])
p["return_rate_pct"] = np.where(p["gross_sales"] > 0, -p["returns_amount"] / p["gross_sales"] * 100, np.nan).round(2) + 0.0   # + 0.0 avoids "-0.0"
p = p.merge(rk[["stock_code", "product_rank", "share_pct", "cum_share_pct"]], on="stock_code", how="left")
p["product_rank"] = p["product_rank"].astype("Int64")                  # blank for products not ranked (dotcom, no sales)
p[["share_pct", "cum_share_pct"]] = p[["share_pct", "cum_share_pct"]].round(4)
dp = p[["stock_code", "product_description", "units_sold", "gross_sales", "returns_amount", "net_product_amount",
        "units_returned", "n_orders", "n_customers", "avg_unit_price", "first_sale_date", "last_sale_date",
        "is_dotcom_code", "is_d13_code", "is_family_79323", "return_rate_pct",
        "product_rank", "share_pct", "cum_share_pct"]]
save(dp, "dim_product.csv")

# ------------------------------------------------------------------ 5. fact_cohort_retention (wide -> long)
mat = pd.read_csv(OUT / "05_cohort_retention.csv", dtype={"cohort": str})
summ = pd.read_csv(OUT / "05_cohort_summary.csv", dtype={"cohort": str})[["cohort", "customers"]]
long = mat.melt(id_vars="cohort", var_name="months_since_first", value_name="active_pct")
long = long.dropna(subset=["active_pct"])                             # blank = month not observable yet
long["months_since_first"] = long["months_since_first"].astype(int)
long = long.merge(summ, on="cohort", how="left")
long["is_base"] = long["cohort"].str.contains("(base)", regex=False).astype(int)
long["cohort"] = long["cohort"].str.extract(r"(\d{4}-\d{2})")[0]
long["cohort_month"] = long["cohort"] + "-01"
long["active_customers"] = (long["active_pct"] * long["customers"] / 100).round().astype(int)
long = long.sort_values(["cohort_month", "months_since_first"])
fc = long[["cohort", "cohort_month", "is_base", "customers", "months_since_first", "active_pct", "active_customers"]]
save(fc, "fact_cohort_retention.csv")

# ------------------------------------------------------------------ 6. Sanity checks (vs cleaning_log / earlier reports)
chk = []


def check(name, got, exp, tol=0.01):
    chk.append({"Check": name, "Computed": f"{got:,.2f}", "Expected": f"{exp:,.2f}",
                "Status": "OK" if abs(got - exp) <= tol else "DIFF"})


nd = fi[fi["is_d13"] == 0]
check("fact_invoices rows", len(fi), 53628, 0)
check("Gross product sales", fi["gross_sales"].sum(), 19700954.46, 0.05)
check("Returns", fi["returns_amount"].sum(), -719692.94, 0.05)
check("Net product revenue", fi["net_product_amount"].sum(), 18981261.52, 0.05)
check("Orders", fi["is_order"].sum(), 39516, 0)
check("Gross excluding D13", nd["gross_sales"].sum(), 19455301.26, 0.05)
check("Returns excluding D13", nd["returns_amount"].sum(), -474039.74, 0.05)
check("D13 invoices flagged", fi["is_d13"].sum(), 4, 0)
check("dim_calendar rows", len(cal), 739, 0)
check("dim_customer rows (customers with orders)", len(dcu), 5852, 0)
# 16,411,894.75 (step 5, incl. 23 cancel-only customers) + 1,406.13 = customers with orders; tol covers 2-decimal rounding in step 5 CSV
check("dim_customer net revenue (customers with orders)", dcu["net_revenue"].sum(), 16411894.75 + 1406.13, 0.05)
seg_now = dcu.groupby("segment")["customer_id"].size()
seg_ref = seg_file.set_index("segment")["customers"]
check("Segments: customers per segment vs 04_segment_summary.csv (sum of abs diff)",
      float((seg_now.reindex(seg_ref.index).fillna(0) - seg_ref).abs().sum()), 0, 0)
check("dim_product rows", len(dp), 4739, 0)
check("dim_product gross sales", dp["gross_sales"].sum(), 19700954.46, 0.05)
check("dim_product returns", dp["returns_amount"].sum(), -719692.94, 0.05)
check("Cohorts exported", fc["cohort"].nunique(), 24, 0)
check("Base cohort (2009-12) customers", fc.loc[fc["is_base"] == 1, "customers"].iloc[0], 951, 0)
check("Cohort month 0 = 100%", float(fc.loc[fc["months_since_first"] == 0, "active_pct"].min()), 100, 0.01)
checks = pd.DataFrame(chk)

# Referential integrity (information, not a pass/fail check)
cid_fact = set(fi["customer_id"].dropna().astype(int))
cid_dim = set(dcu["customer_id"].astype(int))
n_anon = int((fi["has_customer"] == 0).sum())
n_no_dim = len(cid_fact - cid_dim)
n_ctry = len(set(fi["country"].dropna()) - set(dc["country"]))

# ------------------------------------------------------------------ 7. Report
rel = pd.DataFrame([
    ("fact_invoices[invoice_date]", "dim_calendar[date]", "many-to-one"),
    ("fact_invoices[country]", "dim_country[country]", "many-to-one"),
    ("fact_invoices[customer_id]", "dim_customer[customer_id]", "many-to-one (blank for anonymous orders)"),
    ("fact_cohort_retention", "no relationship (stand-alone table for the cohort page)", "-"),
    ("dim_product", "no relationship (aggregated over the whole period, no date)", "-"),
], columns=["from", "to", "type"])

report = "\n".join([
    "# Step 8a - Power BI export", "",
    "## Sanity checks", md(checks), "",
    "## Files written (folder: powerbi/)", md(pd.DataFrame(written)), "",
    "## Referential integrity (information)",
    f"- Invoices without Customer ID (blank customer_id): {n_anon:,}",
    f"- Customer IDs in fact_invoices but not in dim_customer (cancel-only customers and IDs outside customers.csv): {n_no_dim}",
    f"- Countries in fact_invoices but not in dim_country: {n_ctry}", "",
    "## Suggested relationships in the Power BI model", md(rel), "",
])
(OUT / "07_powerbi_export_report.md").write_text(report, encoding="utf-8")
print(f"Done. Files written to: {PBI.resolve()}")
print(checks.to_string(index=False))
