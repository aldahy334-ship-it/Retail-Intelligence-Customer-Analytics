#!/usr/bin/env python3
"""
02_products.py  -  Step 3: Which products drive revenue? (Pareto, top products, returns)

Reads : <in>/products.csv                            (default: clean_output/model)
Writes: analysis_output/02_product_ranking.csv
        analysis_output/02_pareto_curve.png
        analysis_output/02_top_products.png
        analysis_output/02_products_report.md

Analytical decisions (see cleaning_log.md):
  * Products are ranked by NET product revenue, not gross. Gross would put stock code 23843
    (one 168K order cancelled 12 minutes later, D13) at the top, which is misleading.
  * is_dotcom_code products (DCGS*) are excluded from rankings: no customer IDs, tiny value.
    Their share is reported so the exclusion is transparent.
  * Only products with gross sales > 0 count as "sold" (returns-only codes are left out).
  * Return-rate rankings need a minimum order count, otherwise 1 return on 2 sales = 50% is noise.
  * The two D13 stock codes are left out of return rankings (their cancellations are artefacts).

Usage:  python 02_products.py [--in clean_output/model] [--out analysis_output]
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

D13_CODES = ["23843", "23166"]
D13_VALUE = 245_653.20                     # value of the two D13 order/cancellation pairs (verified in step 1)
MIN_ORDERS = 50                            # minimum orders for a return-rate ranking
EXPECTED = {"gross_sales": 19_700_954.46, "returns_amount": -719_692.94,
            "net_product_amount": 18_981_261.52}          # cleaning_log.md (D2)

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


# ------------------------------------------------------------------ 1. Load + sanity checks
p = pd.read_csv(IN / "products.csv", dtype={"stock_code": str}, low_memory=False)
p["is_dotcom_code"] = p["is_dotcom_code"].astype(str).str.lower().eq("true")

checks = pd.DataFrame(
    [[k, f"{p[k].sum():,.2f}", f"{v:,.2f}", "OK" if abs(p[k].sum() - v) <= 0.011 else "DIFF"]
     for k, v in EXPECTED.items()], columns=["Check (sum over products)", "Computed", "Expected", "Status"])

# ------------------------------------------------------------------ 2. Ranking base
sold = p[p["gross_sales"] > 0]
dot = sold[sold["is_dotcom_code"]]
base = (sold[~sold["is_dotcom_code"]]
        .sort_values("net_product_amount", ascending=False).reset_index(drop=True))

total = base["net_product_amount"].sum()
base["share_pct"] = base["net_product_amount"] / total * 100
base["cum_share_pct"] = base["share_pct"].cumsum()
base["pct_of_products"] = (base.index + 1) / len(base) * 100
base["return_rate_pct"] = -base["returns_amount"] / base["gross_sales"] * 100


def n_for(target):
    """Smallest number of top products whose cumulative share reaches `target` %."""
    return int((base["cum_share_pct"] >= target).idxmax()) + 1


n50, n80 = n_for(50), n_for(80)
top10, top100 = base.loc[:9, "share_pct"].sum(), base.loc[:99, "share_pct"].sum()
non_positive = int((base["net_product_amount"] <= 0).sum())
base.round(4).to_csv(OUT / "02_product_ranking.csv", index=False)

# ------------------------------------------------------------------ 3. Returns
r = base[~base["stock_code"].isin(D13_CODES)]
by_rate = r[r["n_orders"] >= MIN_ORDERS].nlargest(10, "return_rate_pct")
by_abs = r.nsmallest(10, "returns_amount")
overall_rate = (-p["returns_amount"].sum() - D13_VALUE) / (p["gross_sales"].sum() - D13_VALUE) * 100

# ------------------------------------------------------------------ 4. Charts
fig, ax = plt.subplots(figsize=(8, 5))
x80 = n80 / len(base) * 100
ax.plot(base["pct_of_products"], base["cum_share_pct"], color="#2f5d8a", lw=2)
ax.axhline(80, ls="--", color="gray"); ax.axvline(x80, ls="--", color="gray")
ax.annotate(f"{n80:,} products ({x80:.1f}%)\n= 80% of net revenue", xy=(x80, 80), xytext=(x80 + 15, 55),
            arrowprops=dict(arrowstyle="->"))
ax.set(xlim=(0, 100), ylim=(0, 105), xlabel="% of products (ranked by net revenue)",
       ylabel="Cumulative % of net product revenue", title="Product revenue concentration (Pareto)")
ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(OUT / "02_pareto_curve.png", dpi=150); plt.close(fig)

t = base.head(15).iloc[::-1]
labels = [f"{str(d)[:35]} ({c})" for d, c in zip(t["product_description"], t["stock_code"])]
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(labels, t["net_product_amount"] / 1e3, color="#2f5d8a")
ax.set(xlabel="Net product revenue (K, presumed GBP)", title="Top 15 products by net revenue")
ax.grid(axis="x", alpha=.3); fig.tight_layout(); fig.savefig(OUT / "02_top_products.png", dpi=150); plt.close(fig)

# ------------------------------------------------------------------ 5. Report
def show(df, cols):
    d = df[cols].copy()
    d.insert(0, "net_rank", df.index + 1)      # position in the NET revenue ranking
    for c in d.columns:
        if d[c].dtype.kind == "f":
            d[c] = d[c].round(2)
    return d


top15 = base.head(15).copy()
top15["product_description"] = [str(d)[:40] + (" *D13" if c in D13_CODES else "")
                                for d, c in zip(top15["product_description"], top15["stock_code"])]
cols_top = ["stock_code", "product_description", "net_product_amount", "share_pct", "cum_share_pct",
            "units_sold", "n_orders", "n_customers", "return_rate_pct"]
cols_ret = ["stock_code", "product_description", "gross_sales", "returns_amount", "return_rate_pct", "n_orders"]

report = "\n".join([
    "# Step 3 - Products", "",
    "## Sanity checks", md(checks), "",
    "## Concentration (Pareto, ranked by net revenue)",
    f"- Products sold (gross > 0, excluding dotcom codes): **{len(base):,}**",
    f"- Top 10 products = **{top10:.1f}%** of net revenue; top 100 = **{top100:.1f}%**",
    f"- 50% of net revenue comes from **{n50:,}** products ({n50 / len(base) * 100:.1f}%)",
    f"- 80% of net revenue comes from **{n80:,}** products ({x80:.1f}%)",
    f"- Products with net revenue <= 0: {non_positive:,}",
    f"- Dotcom codes excluded: {len(dot):,} products, gross {dot['gross_sales'].sum():,.2f} "
    f"({dot['gross_sales'].sum() / p['gross_sales'].sum() * 100:.3f}% of total gross)", "",
    "## Top 15 products by net revenue (*D13 = affected by the cancelled mega-orders)",
    md(show(top15, cols_top)), "",
    f"## Returns (overall return rate excluding D13 pairs: {overall_rate:.2f}% of gross)",
    f"### Top 10 by return rate (products with >= {MIN_ORDERS} orders)", md(show(by_rate, cols_ret)), "",
    "### Top 10 by returned value", md(show(by_abs, cols_ret)), "",
])
(OUT / "02_products_report.md").write_text(report, encoding="utf-8")
print(f"Done. Files written to: {OUT.resolve()}")
print(checks.to_string(index=False))
