#!/usr/bin/env python3
"""
04_customers.py  -  Step 5: Customers (RFM, revenue concentration, segments, anonymous orders)

Reads : <in>/invoices.csv, <in>/customers.csv          (default: clean_output/model)
Writes: analysis_output/04_customer_rfm.csv
        analysis_output/04_segment_summary.csv
        analysis_output/04_revenue_concentration.png
        analysis_output/04_segments.png
        analysis_output/04_top_customers.png
        analysis_output/04_customers_report.md

Analytical decisions (see cleaning_log.md):
  * Only identified customers (D9). Orders without a Customer ID are measured separately,
    so we know how much revenue the customer analysis cannot see.
  * Customer metrics are built from the invoices table (one row per invoice), then reconciled
    with customers.csv in the sanity checks.
  * Recency  = days from the customer's LAST ORDER (sale invoice) to snapshot = last data day + 1.
    Frequency = number of orders. Monetary = NET product revenue (gross + returns).
    Net is used because the two D13 mega-orders are cancelled and net to zero; gross would
    rank their customers at the top for revenue that never stayed.
  * Customers with only cancellations (no order) have no Recency/Frequency: excluded from RFM.
  * Scores 1-5 (5 = best). R and M use quintiles of the rank (ties broken by order of appearance).
    F uses fixed bins (FREQ_BINS) because most customers share the same few order counts,
    and quintiles on ties would split identical customers into different scores.
  * Segment names are descriptive labels from simple R/F rules, not proven behaviour.

Usage:  python 04_customers.py [--in clean_output/model] [--out analysis_output]
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BLUE, ORANGE = "#2f5d8a", "#e08e2b"
D13_SALE_INVOICES = ["581483", "541431"]
CUST_12346 = 12346
FREQ_BINS = [0, 1, 2, 4, 9, np.inf]          # orders -> F score 1..5  (1 | 2 | 3-4 | 5-9 | 10+)
SEGMENT_ORDER = ["Champions", "Loyal", "New / Promising", "Needs Attention", "At Risk", "Hibernating"]

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
cust = pd.read_csv(IN / "customers.csv", low_memory=False)
inv["invoice_ts"] = pd.to_datetime(inv["invoice_ts"])
inv["customer_id"] = pd.to_numeric(inv["customer_id"], errors="coerce").astype("Int64")
cust["customer_id"] = pd.to_numeric(cust["customer_id"]).astype("Int64")

orders = inv[inv["n_sale_lines"] > 0]                         # an order = invoice with >= 1 sale line
orders_adj = orders[~orders["invoice"].isin(D13_SALE_INVOICES)]
ident = inv[inv["customer_id"].notna()]
snapshot = inv["invoice_ts"].max().normalize() + pd.Timedelta(days=1)

# ------------------------------------------------------------------ 2. Customer table
g = ident.groupby("customer_id")
og = orders[orders["customer_id"].notna()].groupby("customer_id")
c = pd.DataFrame({
    "orders": og["invoice"].nunique(),
    "first_order_ts": og["invoice_ts"].min(),
    "last_order_ts": og["invoice_ts"].max(),
    "gross_sales": g["gross_sales"].sum(),
    "returns_amount": g["returns_amount"].sum(),
    "net_revenue": g["net_product_amount"].sum(),
    "n_cancel_invoices": ident[ident["n_cancel_lines"] > 0].groupby("customer_id")["invoice"].nunique(),
})
c[["orders", "n_cancel_invoices"]] = c[["orders", "n_cancel_invoices"]].fillna(0).astype(int)
n_ids_in_invoices = len(c)
c = c[c.index.isin(cust["customer_id"])]                      # same population as customers.csv
n_extra_ids = n_ids_in_invoices - len(c)
c = c.join(cust.set_index("customer_id")[["country"]])

# ------------------------------------------------------------------ 3. RFM
r = c[c["orders"] > 0].copy()
r["recency_days"] = (snapshot - r["last_order_ts"].dt.normalize()).dt.days


def quintile(s):
    return pd.qcut(s.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)


r["R"] = 6 - quintile(r["recency_days"])                      # fewer days since last order = better
r["F"] = pd.cut(r["orders"], FREQ_BINS, labels=[1, 2, 3, 4, 5]).astype(int)
r["M"] = quintile(r["net_revenue"])
r["rfm_code"] = r["R"].astype(str) + r["F"].astype(str) + r["M"].astype(str)
R_, F_ = r["R"], r["F"]
r["segment"] = np.select(
    [(R_ >= 4) & (F_ >= 4), (R_ >= 3) & (F_ >= 3), (R_ >= 4) & (F_ <= 2),
     (R_ <= 2) & (F_ >= 3), (R_ <= 2) & (F_ <= 2)],
    ["Champions", "Loyal", "New / Promising", "At Risk", "Hibernating"],
    default="Needs Attention")

tot_net_all = inv["net_product_amount"].sum()
tot_net_id = r["net_revenue"].sum()

seg = r.groupby("segment").agg(customers=("orders", "size"), net_revenue=("net_revenue", "sum"),
                               median_orders=("orders", "median"),
                               median_recency_days=("recency_days", "median"))
seg = seg.reindex([s for s in SEGMENT_ORDER if s in seg.index])
seg["customers_pct"] = seg["customers"] / len(r) * 100
seg["net_share_pct"] = seg["net_revenue"] / tot_net_id * 100
seg["net_per_customer"] = seg["net_revenue"] / seg["customers"]
seg = seg[["customers", "customers_pct", "net_revenue", "net_share_pct", "net_per_customer",
           "median_orders", "median_recency_days"]]
seg.round(2).to_csv(OUT / "04_segment_summary.csv", index_label="segment")


def span(col, score_col, fmt):
    a = r.groupby(score_col)[col].agg(["min", "max"])
    return a.apply(lambda x: f"{fmt(x['min'])} to {fmt(x['max'])}", axis=1)


scores = pd.DataFrame({
    "score": [1, 2, 3, 4, 5],
    "R_days_since_last_order": span("recency_days", "R", lambda v: f"{v:,.0f}"),
    "F_orders": span("orders", "F", lambda v: f"{v:,.0f}"),
    "M_net_revenue": span("net_revenue", "M", lambda v: f"{v:,.0f}"),
}, index=[1, 2, 3, 4, 5]).reset_index(drop=True)
scores["customers_R"] = r["R"].value_counts().reindex([1, 2, 3, 4, 5]).fillna(0).astype(int).values
scores["customers_F"] = r["F"].value_counts().reindex([1, 2, 3, 4, 5]).fillna(0).astype(int).values
scores["customers_M"] = r["M"].value_counts().reindex([1, 2, 3, 4, 5]).fillna(0).astype(int).values

out_cols = ["country", "orders", "first_order_ts", "last_order_ts", "recency_days", "gross_sales",
            "returns_amount", "net_revenue", "n_cancel_invoices", "R", "F", "M", "rfm_code", "segment"]
rfm_out = r[out_cols].sort_values("net_revenue", ascending=False)
num_cols = ["gross_sales", "returns_amount", "net_revenue"]
rfm_out[num_cols] = rfm_out[num_cols].round(2)
rfm_out.to_csv(OUT / "04_customer_rfm.csv", index_label="customer_id")

# ------------------------------------------------------------------ 4. Concentration (identified customers)
s = r["net_revenue"].sort_values(ascending=False).reset_index(drop=True)
n = len(s)
cum = s.cumsum() / s.sum()
rows = []
for p in (0.01, 0.05, 0.10, 0.20):
    k = int(np.ceil(n * p))
    top = s.iloc[:k].sum()
    rows.append({"top_group": f"Top {p:.0%}", "customers": k, "net_revenue": round(top, 2),
                 "share_of_identified_net_pct": round(top / s.sum() * 100, 2),
                 "share_of_total_net_pct": round(top / tot_net_all * 100, 2)})
conc = pd.DataFrame(rows)
n50 = int((cum >= 0.5).idxmax() + 1)
n80 = int((cum >= 0.8).idxmax() + 1)

# ------------------------------------------------------------------ 5. Anonymous vs identified orders
anon_mask = inv["customer_id"].isna()


def block(name, mask):
    o = orders[mask.reindex(orders.index)]
    oa = orders_adj[mask.reindex(orders_adj.index)]
    return {"group": name, "orders": len(o), "orders_pct": len(o) / len(orders) * 100,
            "gross_sales": inv.loc[mask, "gross_sales"].sum(),
            "net_revenue": inv.loc[mask, "net_product_amount"].sum(),
            "net_share_pct": inv.loc[mask, "net_product_amount"].sum() / tot_net_all * 100,
            "median_order_value": o["gross_sales"].median(),
            "mean_order_value_ex_d13": oa["gross_sales"].mean()}


anon_tbl = pd.DataFrame([block("Identified", ~anon_mask), block("Anonymous (no Customer ID)", anon_mask)])

# ------------------------------------------------------------------ 6. D13 customers and customer 12346
d13_ids = inv.loc[inv["invoice"].isin(D13_SALE_INVOICES), "customer_id"].dropna().unique().tolist()
focus = []
for cid in dict.fromkeys([CUST_12346] + d13_ids):             # unique, keeps order
    if cid in r.index:
        focus.append(cid)
r["rank_by_gross"] = r["gross_sales"].rank(ascending=False, method="min").astype(int)
r["rank_by_net"] = r["net_revenue"].rank(ascending=False, method="min").astype(int)
d13_note = []
for inv_no in D13_SALE_INVOICES:
    v = inv.loc[inv["invoice"] == inv_no, "customer_id"]
    who = "not found" if v.empty else ("anonymous (no Customer ID)" if v.isna().all() else f"customer {int(v.iloc[0])}")
    d13_note.append(f"- Invoice {inv_no}: {who}")
f_tbl = r.loc[focus, ["orders", "gross_sales", "returns_amount", "net_revenue", "n_cancel_invoices",
                      "rank_by_gross", "rank_by_net", "segment"]].round(2).reset_index()

# ------------------------------------------------------------------ 7. Sanity checks
chk = []


def check(name, got, exp, tol=0.01):
    ok = abs(got - exp) <= tol
    chk.append({"Check": name, "Computed": f"{got:,.2f}", "Expected": f"{exp:,.2f}", "Status": "OK" if ok else "DIFF"})


check("Customers in customers table", len(cust), 5875)
check("Customers with at least one order", int((c["orders"] > 0).sum()), 5852)
check("Customers with cancellations only", int((c["orders"] == 0).sum()), 23)
check("Orders", len(orders), 39516)
check("Gross product sales (invoices)", inv["gross_sales"].sum(), 19700954.46)
check("Returns (invoices)", inv["returns_amount"].sum(), -719692.94)
check("Net product revenue (invoices)", tot_net_all, 18981261.52)
check("Identified net: invoices vs customers.csv", c["net_revenue"].sum(), cust["net_product_amount"].sum())
check("Identified orders: invoices vs customers.csv (n_orders)", c["orders"].sum(), cust["n_orders"].sum())
chk.append({"Check": "Snapshot date (last data day + 1)", "Computed": str(snapshot.date()),
            "Expected": "2011-12-10", "Status": "OK" if str(snapshot.date()) == "2011-12-10" else "DIFF"})
for label, col, exp in (("Customer 12346 gross (brief value is rounded, tol 1)", "gross_sales", 77353),
                        ("Customer 12346 returns (brief value is rounded, tol 1)", "returns_amount", -77184),
                        ("Customer 12346 net (brief value is rounded, tol 1)", "net_revenue", 169)):
    check(label, c.loc[CUST_12346, col] if CUST_12346 in c.index else np.nan, exp, tol=1.0)
checks = pd.DataFrame(chk)

# ------------------------------------------------------------------ 8. Charts
fig, ax = plt.subplots(figsize=(7, 5))
x = np.arange(1, n + 1) / n * 100
ax.plot(x, cum.values * 100, color=BLUE, lw=2, label="Cumulative net revenue")
ax.plot([0, 100], [0, 100], color="grey", ls="--", lw=1, label="Perfect equality")
for p in (0.01, 0.10):
    k = int(np.ceil(n * p))
    ax.scatter([k / n * 100], [cum.iloc[k - 1] * 100], color=ORANGE, zorder=3)
    ax.annotate(f"Top {p:.0%}: {cum.iloc[k - 1] * 100:.0f}%", (k / n * 100, cum.iloc[k - 1] * 100),
                textcoords="offset points", xytext=(10, -14), fontsize=9)
ax.set_xlabel("Share of identified customers (ranked by net revenue, %)")
ax.set_ylabel("Cumulative share of net revenue (%)")
ax.set_title("Revenue concentration across identified customers")
ax.grid(alpha=.3); ax.legend(loc="lower right")
fig.tight_layout(); fig.savefig(OUT / "04_revenue_concentration.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4.5))
pos = np.arange(len(seg)); w = 0.38
ax.barh(pos - w / 2, seg["customers_pct"], w, color=BLUE, label="% of customers")
ax.barh(pos + w / 2, seg["net_share_pct"], w, color=ORANGE, label="% of net revenue")
ax.set_yticks(pos); ax.set_yticklabels(seg.index); ax.invert_yaxis()
ax.set_xlabel("Share (%)"); ax.set_title("RFM segments: share of customers vs share of net revenue")
ax.grid(axis="x", alpha=.3); ax.legend()
fig.tight_layout(); fig.savefig(OUT / "04_segments.png", dpi=150); plt.close(fig)

top15 = r.sort_values("net_revenue", ascending=False).head(15)
fig, ax = plt.subplots(figsize=(8, 5.5))
labels = [f"{i} ({cn})" for i, cn in zip(top15.index, top15["country"])]
ax.barh(labels, top15["net_revenue"], color=BLUE)
ax.invert_yaxis(); ax.set_xlabel("Net product revenue (GBP)")
ax.set_title("Top 15 customers by net revenue")
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:,.0f}K"))
ax.grid(axis="x", alpha=.3)
fig.tight_layout(); fig.savefig(OUT / "04_top_customers.png", dpi=150); plt.close(fig)

# ------------------------------------------------------------------ 9. Report
beh = pd.DataFrame([
    ("Customers with at least one order", f"{len(r):,}"),
    ("One-time customers (1 order)", f"{(r['orders'] == 1).mean() * 100:.1f}%"),
    ("Repeat customers (2+ orders)", f"{(r['orders'] >= 2).mean() * 100:.1f}%"),
    ("Median orders per customer", f"{r['orders'].median():.0f}"),
    ("Median net revenue per customer", f"{r['net_revenue'].median():,.2f}"),
    ("Mean net revenue per customer", f"{r['net_revenue'].mean():,.2f}"),
    ("Median days since last order", f"{r['recency_days'].median():.0f}"),
    ("Customers with net revenue <= 0", f"{int((r['net_revenue'] <= 0).sum())}"),
], columns=["Metric", "Value"])

t15 = r.sort_values("net_revenue", ascending=False).head(15).copy()
t15["avg_order_value"] = t15["gross_sales"] / t15["orders"]
t15["share_of_identified_net_pct"] = t15["net_revenue"] / tot_net_id * 100
t15["last_order"] = t15["last_order_ts"].dt.date
t15 = t15[["country", "orders", "net_revenue", "share_of_identified_net_pct", "avg_order_value",
           "last_order", "recency_days", "segment"]].round(2).reset_index()
t15["customer_id"] = [f"{i}{' *' if i in d13_ids else ''}" for i in t15["customer_id"]]

seg_t = seg.round(2).reset_index()
anon_t = anon_tbl.round(2)
rules = pd.DataFrame([
    ("Champions", "R >= 4 and F >= 4"), ("Loyal", "R >= 3 and F >= 3 (not Champions)"),
    ("New / Promising", "R >= 4 and F <= 2"), ("Needs Attention", "R = 3 and F <= 2"),
    ("At Risk", "R <= 2 and F >= 3"), ("Hibernating", "R <= 2 and F <= 2")],
    columns=["segment", "rule"])

report = "\n".join([
    "# Step 5 - Customers", "",
    "## Sanity checks", md(checks), "",
    f"- Customer IDs present in invoices but not in customers.csv: {n_extra_ids}",
    f"- Snapshot date for Recency: {snapshot.date()}  (data ends {inv['invoice_ts'].max().date()})", "",
    "## Customer behaviour (identified customers with orders)", md(beh), "",
    "## Revenue concentration (identified customers, ranked by net revenue)", md(conc), "",
    f"- 50% of identified net revenue comes from **{n50:,}** customers ({n50 / n * 100:.1f}%)",
    f"- 80% of identified net revenue comes from **{n80:,}** customers ({n80 / n * 100:.1f}%)", "",
    "## RFM scores (score 5 = best; ranges computed from the data)", md(scores), "",
    "## Segments: rules", md(rules), "",
    "- Rules are applied in the order Champions, Loyal, New / Promising, At Risk, Hibernating; the remainder is Needs Attention.", "",
    "## Segments: summary", md(seg_t), "",
    "## Top 15 customers by net revenue (* = customer of a D13 mega-order)", md(t15), "",
    "## Customer 12346 and the D13 customers: gross rank vs net rank", md(f_tbl), "",
    *d13_note, "",
    "## Anonymous orders: how much revenue does the customer analysis not see?", md(anon_t), "",
    "- Net revenue per group includes the cancellation invoices of that group.",
    "- mean_order_value_ex_d13 excludes invoices 581483 and 541431.", "",
])
(OUT / "04_customers_report.md").write_text(report, encoding="utf-8")
print(f"Done. Files written to: {OUT.resolve()}")
print(checks.to_string(index=False))
