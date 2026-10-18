#!/usr/bin/env python3
"""
01_time_trend.py  -  Step 2: Revenue over time (monthly trend & seasonality)

Reads : <in>/invoices.csv, <in>/calendar.csv        (default: clean_output/model)
Writes: analysis_output/01_monthly_metrics.csv
        analysis_output/01_monthly_trend.png
        analysis_output/01_yoy_by_month.png
        analysis_output/01_time_trend_report.md

Analytical decisions (see cleaning_log.md):
  * Base data keeps flagged duplicate rows (D2).
  * Headline metric = Net product revenue (gross + returns).
  * The two D13 order/cancellation pairs are excluded from Gross/Returns views only;
    they cancel out inside the same month, so Net revenue is identical either way.
  * Months flagged is_partial_month (Dec 2011) are plotted but excluded from comparisons.
  * Order value is summarised by the MEDIAN, which is robust to wholesale mega-orders.

Usage:  python 01_time_trend.py [--in clean_output/model] [--out analysis_output]
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                      # render to file, no window needed
import matplotlib.pyplot as plt
import pandas as pd

D13_INVOICES = ["581483", "C581484", "541431", "C541433"]
EXPECTED_GROSS, EXPECTED_ORDERS = 19_700_954.46, 39_516     # from cleaning_log.md (D2)

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="indir", default="clean_output/model")
ap.add_argument("--out", default="analysis_output")
args = ap.parse_args()
IN, OUT = Path(args.indir), Path(args.out)
OUT.mkdir(parents=True, exist_ok=True)


def md(df):
    """Minimal Markdown table (no tabulate dependency)."""
    cols = [str(c) for c in df.columns]
    rows = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    rows += ["| " + " | ".join(map(str, r)) + " |" for r in df.itertuples(index=False)]
    return "\n".join(rows)


# ------------------------------------------------------------------ 1. Load
inv = pd.read_csv(IN / "invoices.csv", dtype={"invoice": str}, low_memory=False)
cal = pd.read_csv(IN / "calendar.csv")
inv["month"] = pd.to_datetime(inv["invoice_ts"]).dt.to_period("M").astype(str)
partial = set(cal.loc[cal["is_partial_month"], "year_month"])

sales = inv[inv["n_sale_lines"] > 0]                      # "Orders" definition (cleaning_log s.6)
adj = inv[~inv["invoice"].isin(D13_INVOICES)]             # without the D13 pairs

# ------------------------------------------------------------------ 2. Sanity checks
checks = pd.DataFrame([
    ["Gross product sales", f"{inv['gross_sales'].sum():,.2f}", f"{EXPECTED_GROSS:,.2f}",
     "OK" if round(inv["gross_sales"].sum(), 2) == EXPECTED_GROSS else "DIFF"],
    ["Orders", f"{sales['invoice'].nunique():,}", f"{EXPECTED_ORDERS:,}",
     "OK" if sales["invoice"].nunique() == EXPECTED_ORDERS else "DIFF"],
    ["Net revenue: with vs without D13 pairs (difference)",
     f"{inv['net_product_amount'].sum() - adj['net_product_amount'].sum():,.2f}", "0.00",
     "OK" if round(inv["net_product_amount"].sum() - adj["net_product_amount"].sum(), 2) == 0 else "DIFF"],
], columns=["Check", "Computed", "Expected", "Status"])

# ------------------------------------------------------------------ 3. Monthly metrics
m = pd.DataFrame({
    "net_revenue": inv.groupby("month")["net_product_amount"].sum(),
    "gross_ex_d13": adj.groupby("month")["gross_sales"].sum(),
    "returns_ex_d13": adj.groupby("month")["returns_amount"].sum(),
    "orders": sales.groupby("month")["invoice"].nunique(),
    "active_customers": sales.groupby("month")["customer_id"].nunique(),
    "median_order_value": sales.groupby("month")["gross_sales"].median(),
}).sort_index()
m["partial"] = m.index.isin(partial)
m.round(2).to_csv(OUT / "01_monthly_metrics.csv", index_label="month")
full = m[~m["partial"]]                                   # complete months only

# ------------------------------------------------------------------ 4. Period comparison
P1, P2 = ("2009-12", "2010-11"), ("2010-12", "2011-11")   # two full 12-month periods


def period(lo, hi):
    f = full.loc[lo:hi]
    s = sales[sales["month"].between(lo, hi)]
    q = f.index.str[-2:].isin(["09", "10", "11"])
    return {"Net revenue": f["net_revenue"].sum(), "Orders": f["orders"].sum(),
            "Active customers": s["customer_id"].nunique(),
            "Sep-Nov share of net revenue (%)": f.loc[q, "net_revenue"].sum() / f["net_revenue"].sum() * 100}


a1, a2 = period(*P1), period(*P2)
cmp_df = pd.DataFrame([
    [k, f"{a1[k]:,.1f}", f"{a2[k]:,.1f}",
     f"{a2[k] - a1[k]:+.1f} pp" if "share" in k else f"{(a2[k] / a1[k] - 1) * 100:+.1f}%"]
    for k in a1], columns=["Metric", "Dec09-Nov10", "Dec10-Nov11", "Change"])
peak = full["net_revenue"].idxmax()

# ------------------------------------------------------------------ 5. Charts
fig, ax = plt.subplots(2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
bars = ax[0].bar(m.index, m["net_revenue"] / 1e3, color="#2f5d8a")
for b, p in zip(bars, m["partial"]):
    if p:
        b.set_facecolor("#b0b7c3"); b.set_hatch("//")
ax[0].set_ylabel("Net product revenue (K, presumed GBP)")
ax[0].set_title("Monthly net product revenue (hatched = partial month)")
ax[1].plot(m.index, m["orders"], marker="o", label="Orders")
ax[1].plot(m.index, m["active_customers"], marker="s", label="Active identified customers")
ax[1].legend(); ax[1].set_ylabel("Count"); ax[1].grid(alpha=.3)
plt.setp(ax[1].get_xticklabels(), rotation=90)
fig.text(0.01, 0.005, "Data ends 2011-12-09. Net revenue is unaffected by the two D13 order/cancellation pairs.",
         fontsize=8, color="gray")
fig.tight_layout(); fig.savefig(OUT / "01_monthly_trend.png", dpi=150); plt.close(fig)

t = full["net_revenue"].copy()
t.index = pd.MultiIndex.from_tuples([(int(s[:4]), int(s[5:])) for s in t.index], names=["year", "month"])
pv = t.unstack(0)[[2010, 2011]] / 1e3                     # rows = calendar month, cols = year
ax2 = pv.plot(marker="o", figsize=(9, 5), title="Net revenue by calendar month: 2010 vs 2011 (complete months)")
ax2.set_xticks(range(1, 13)); ax2.set_xlabel("Month"); ax2.set_ylabel("Net revenue (K)"); ax2.grid(alpha=.3)
ax2.figure.tight_layout(); ax2.figure.savefig(OUT / "01_yoy_by_month.png", dpi=150); plt.close(ax2.figure)

# ------------------------------------------------------------------ 6. Report
tbl = m.round(2).reset_index().rename(columns={"index": "month"})
tbl["partial"] = tbl["partial"].map({True: "partial", False: ""})
report = "\n".join([
    "# Step 2 - Revenue over time", "",
    "## Sanity checks", md(checks), "",
    "## Full-year comparison (complete 12-month periods)", md(cmp_df), "",
    f"- Peak month by net revenue (complete months): **{peak}** ({full.loc[peak, 'net_revenue']:,.2f})",
    f"- Partial months excluded from comparisons: {sorted(partial)}", "",
    "## Monthly metrics", md(tbl), "",
])
(OUT / "01_time_trend_report.md").write_text(report, encoding="utf-8")
print(f"Done. Files written to: {OUT.resolve()}")
print(checks.to_string(index=False))
