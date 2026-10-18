#!/usr/bin/env python3
"""
03_countries.py  -  Step 4: Markets (UK vs international, top countries, growth)

Reads : <in>/invoices.csv, <in>/calendar.csv          (default: clean_output/model)
Writes: analysis_output/03_country_metrics.csv
        analysis_output/03_uk_vs_intl_monthly.csv
        analysis_output/03_top_markets.png
        analysis_output/03_market_growth.png
        analysis_output/03_uk_vs_intl_monthly.png
        analysis_output/03_countries_report.md

Analytical decisions (see cleaning_log.md):
  * Country comes from the invoice (every invoice has exactly one country), so the 12 customers
    seen in two countries (D14) do not affect country revenue.
  * Revenue = NET product revenue. The D13 mega-orders are both UK and net to zero.
  * Order value: median (robust) + mean excluding the two D13 orders.
  * Growth compares the same two complete 12-month periods as step 2 (partial Dec 2011 excluded),
    and only for countries with at least MIN_BASE net revenue in the first period (tiny bases
    produce meaningless percentages).
  * 'Unspecified' and 'European Community' are generic labels (D14): kept, marked with *.

Usage:  python 03_countries.py [--in clean_output/model] [--out analysis_output]
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

UK = "United Kingdom"
D13_SALE_INVOICES = ["581483", "541431"]
GENERIC = {"Unspecified", "European Community"}
MIN_BASE = 25_000
P1, P2 = ("2009-12", "2010-11"), ("2010-12", "2011-11")
EXPECTED = {"Net revenue": 18_981_261.52, "Orders": 39_516,
            "Net revenue P1 (step 2)": 9_188_552.6, "Net revenue P2 (step 2)": 9_351_342.4}

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
inv["grp"] = inv["country"].eq(UK).map({True: "UK", False: "International"})
partial = set(cal.loc[cal["is_partial_month"], "year_month"])
sales = inv[inv["n_sale_lines"] > 0]                                   # orders
sales_adj = sales[~sales["invoice"].isin(D13_SALE_INVOICES)]           # orders without D13


def net_in(by, lo, hi):
    return inv[inv["month"].between(lo, hi)].groupby(by)["net_product_amount"].sum()


# ------------------------------------------------------------------ 2. Country table
c = pd.DataFrame({
    "net_revenue": inv.groupby("country")["net_product_amount"].sum(),
    "orders": sales.groupby("country")["invoice"].nunique(),
    "customers": sales.groupby("country")["customer_id"].nunique(),
    "median_order_value": sales.groupby("country")["gross_sales"].median(),
    "mean_order_value_ex_d13": sales_adj.groupby("country")["gross_sales"].mean(),
    "anon_orders_pct": sales.groupby("country")["customer_id"].apply(lambda s: s.isna().mean() * 100),
})
c[["orders", "customers"]] = c[["orders", "customers"]].fillna(0).astype(int)
cust_net = inv.dropna(subset=["customer_id"]).groupby(["country", "customer_id"])["net_product_amount"].sum()
c["top_customer_share_pct"] = cust_net.groupby("country").max() / c["net_revenue"] * 100   # account concentration
c = c.sort_values("net_revenue", ascending=False)
c["share_pct"] = c["net_revenue"] / c["net_revenue"].sum() * 100
c["cum_share_pct"] = c["share_pct"].cumsum()
c.round(2).to_csv(OUT / "03_country_metrics.csv", index_label="country")

# ------------------------------------------------------------------ 3. UK vs International
def grp_row(name):
    i, s, sa = inv[inv["grp"] == name], sales[sales["grp"] == name], sales_adj[sales_adj["grp"] == name]
    net = i["net_product_amount"].sum()
    return [name, round(net, 2), round(net / inv["net_product_amount"].sum() * 100, 2),
            s["invoice"].nunique(), s["customer_id"].nunique(), round(s["gross_sales"].median(), 2),
            round(sa["gross_sales"].mean(), 2), round(s["customer_id"].isna().mean() * 100, 1)]


grp_df = pd.DataFrame([grp_row("UK"), grp_row("International")],
                      columns=["market", "net_revenue", "share_pct", "orders", "customers",
                               "median_order_value", "mean_order_value_ex_d13", "anon_orders_pct"])

# ------------------------------------------------------------------ 4. Growth (two complete 12-month periods)
g = pd.DataFrame({"P1": net_in("country", *P1), "P2": net_in("country", *P2)}).fillna(0)
gg = pd.DataFrame({"P1": net_in("grp", *P1), "P2": net_in("grp", *P2)}).fillna(0)
gg.loc["Total"] = gg.sum()
ctry = g[(g["P1"] >= MIN_BASE) & (g.index != UK)].copy()
for d in (gg, ctry):
    d["change_pct"] = (d["P2"] / d["P1"] - 1) * 100
growth = pd.concat([gg.reindex(["UK", "International", "Total"]).dropna(),
                    ctry.sort_values("P2", ascending=False)])
growth.index.name = "market"

# ------------------------------------------------------------------ 5. Monthly UK vs International
mp = inv.groupby(["month", "grp"])["net_product_amount"].sum().unstack().fillna(0)
for k in ("UK", "International"):
    if k not in mp:
        mp[k] = 0.0
mp["intl_share_pct"] = mp["International"] / (mp["UK"] + mp["International"]) * 100
mp.round(2).to_csv(OUT / "03_uk_vs_intl_monthly.csv", index_label="month")
full = mp.drop(index=[m for m in partial if m in mp.index])


def intl_share(lo, hi):
    s = mp.loc[lo:hi]
    return s["International"].sum() / (s["UK"].sum() + s["International"].sum()) * 100


# ------------------------------------------------------------------ 6. Sanity checks
rows = []
for name, got, exp in [("Net revenue", inv["net_product_amount"].sum(), EXPECTED["Net revenue"]),
                       ("Orders", sales["invoice"].nunique(), EXPECTED["Orders"]),
                       ("Net revenue P1 (step 2)", gg.loc["Total", "P1"], EXPECTED["Net revenue P1 (step 2)"]),
                       ("Net revenue P2 (step 2)", gg.loc["Total", "P2"], EXPECTED["Net revenue P2 (step 2)"])]:
    ok = abs(got - exp) <= (0 if name == "Orders" else 0.06)
    rows.append([name, f"{got:,.2f}", f"{exp:,.2f}", "OK" if ok else "DIFF"])
checks = pd.DataFrame(rows, columns=["Check", "Computed", "Expected", "Status"])

# ------------------------------------------------------------------ 7. Charts
top_i = c.drop(index=UK, errors="ignore").head(10).iloc[::-1]
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.barh([f"{n}{'*' if n in GENERIC else ''}" for n in top_i.index], top_i["net_revenue"] / 1e3, color="#2f5d8a")
for y, (v, s) in enumerate(zip(top_i["net_revenue"] / 1e3, top_i["share_pct"])):
    ax.text(v, y, f"  {s:.1f}%", va="center", fontsize=8)
uk_share = c.loc[UK, "share_pct"] if UK in c.index else float("nan")
ax.set(xlabel="Net product revenue (K, presumed GBP)",
       title=f"Top 10 international markets (UK = {uk_share:.1f}% of total, not shown)")
ax.grid(axis="x", alpha=.3); fig.tight_layout(); fig.savefig(OUT / "03_top_markets.png", dpi=150); plt.close(fig)

cc = ctry.sort_values("change_pct")
fig, ax = plt.subplots(figsize=(9, 5.5))
CAP = 120                                                  # cap the axis so one huge value does not flatten the rest
ax.barh(cc.index, cc["change_pct"].clip(upper=CAP), color=["#c0392b" if v < 0 else "#2f5d8a" for v in cc["change_pct"]])
for y, v in enumerate(cc["change_pct"]):
    ax.text(min(v, CAP) + (2 if v >= 0 else -2), y, f"{v:+.0f}%" + (" (axis capped)" if v > CAP else ""),
            va="center", ha="left" if v >= 0 else "right", fontsize=8)
ax.set_xlim(min(cc["change_pct"].min() - 20, -20), CAP + 60)
for lab, ls in (("UK", "--"), ("International", ":")):
    if lab in gg.index:
        ax.axvline(gg.loc[lab, "change_pct"], ls=ls, color="gray", label=f"{lab} total ({gg.loc[lab, 'change_pct']:+.1f}%)")
ax.axvline(0, color="black", lw=.8)
ax.set(xlabel="Net revenue change, Dec10-Nov11 vs Dec09-Nov10 (%)",
       title=f"Market growth (countries with >= {MIN_BASE:,} net revenue in first period)")
ax.legend(); ax.grid(axis="x", alpha=.3); fig.tight_layout()
fig.savefig(OUT / "03_market_growth.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(11, 5))
ax.bar(mp.index, mp["UK"] / 1e3, label="UK", color="#2f5d8a")
ax.bar(mp.index, mp["International"] / 1e3, bottom=mp["UK"] / 1e3, label="International", color="#e08e2b")
ax.set(ylabel="Net product revenue (K, presumed GBP)", title="Monthly net revenue: UK vs International (2011-12 is a partial month)")
ax.legend(); plt.setp(ax.get_xticklabels(), rotation=90); fig.tight_layout()
fig.savefig(OUT / "03_uk_vs_intl_monthly.png", dpi=150); plt.close(fig)

# ------------------------------------------------------------------ 8. Report
t = c.head(15).round(2).reset_index().rename(columns={"index": "country"})
t["country"] = [f"{n}{' *' if n in GENERIC else ''}" for n in t["country"]]
gtbl = growth.round(2).reset_index()
gtbl["change_pct"] = gtbl["change_pct"].map(lambda v: f"{v:+.1f}%")
report = "\n".join([
    "# Step 4 - Markets", "",
    "## Sanity checks", md(checks), "",
    "## UK vs International (whole period)", md(grp_df), "",
    "## Top 15 countries by net revenue (* = generic label, see D14)", md(t), "",
    f"## Growth: Dec10-Nov11 vs Dec09-Nov10 (countries with >= {MIN_BASE:,} in the first period)", md(gtbl), "",
    "## International share of net revenue",
    f"- Dec09-Nov10: **{intl_share(*P1):.1f}%** | Dec10-Nov11: **{intl_share(*P2):.1f}%**",
    f"- Monthly range (complete months): {full['intl_share_pct'].min():.1f}% to {full['intl_share_pct'].max():.1f}%",
    f"- Countries in data: {len(c)} | countries covering 90% of net revenue: {int((c['cum_share_pct'] < 90).sum() + 1)}", "",
])
(OUT / "03_countries_report.md").write_text(report, encoding="utf-8")
print(f"Done. Files written to: {OUT.resolve()}")
print(checks.to_string(index=False))
