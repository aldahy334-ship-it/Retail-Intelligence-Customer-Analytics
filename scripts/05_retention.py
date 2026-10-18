#!/usr/bin/env python3
"""
05_retention.py  -  Step 6: Cohorts and retention (+ three open checks from step 5)

Reads : <in>/invoices.csv, <in>/customers.csv, <in>/calendar.csv     (default: clean_output/model)
Writes: analysis_output/05_cohort_retention.csv        (monthly active %, cohort x months since first order)
        analysis_output/05_cohort_summary.csv
        analysis_output/05_retention_heatmap.png
        analysis_output/05_retention_curve.png
        analysis_output/05_repeat_rate.png
        analysis_output/05_cumulative_value.png
        analysis_output/05_retention_report.md

Analytical decisions (see cleaning_log.md):
  * Population: identified customers with at least one order (5,852). Cohort = month of the first
    order observed (first invoice with a sale line).
  * LEFT-CENSORING: the data starts in Dec 2009, so the 2009-12 cohort ("base") mixes new customers with
    customers who already existed. It is shown separately and excluded from the "new customers" averages.
    Some early-2010 "new" customers may also be returning ones (cannot be verified from the data).
  * Monthly retention = share of the cohort that placed at least one order in month k after the first.
    Only COMPLETE months are used (Dec 2011 is partial, D15), so a cell is shown only if cohort + k <= Nov 2011.
  * Wholesale buyers order irregularly, so monthly activity understates loyalty. We therefore also report
    the REPEAT RATE: share of customers with a later-day order within 30/60/90/180/365 days of the first
    one, counted only for customers observable for the whole window (first order + window <= last data day).
    A second invoice on the same calendar day is treated as part of the same visit, not as a repeat.
  * Cumulative value = cumulative net product revenue per acquired customer (returns included).
  * Averages across cohorts are weighted by cohort size and use only cohorts observable at that month.

Open checks from step 5 (appendix of the report):
  A. The customer IDs that exist in invoices.csv but not in customers.csv.
  B. RFM segments re-computed at other snapshot dates (is Recency flattered by the season?).
  C. Growth of the international markets with and without their biggest accounts.

Usage:  python 05_retention.py [--in clean_output/model] [--out analysis_output]
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd

BLUE, ORANGE = "#2f5d8a", "#e08e2b"
BASE_COHORT = "2009-12"
WINDOWS = [30, 60, 90, 180, 365]
HEAT_CAP = 60                                   # heatmap color capped at this % (month 0 is always 100)
P1, P2 = ("2009-12", "2010-11"), ("2010-12", "2011-11")
UK = "United Kingdom"
FREQ_BINS = [0, 1, 2, 4, 9, np.inf]             # same as step 5
SEGMENT_ORDER = ["Champions", "Loyal", "New / Promising", "Needs Attention", "At Risk", "Hibernating"]
SNAPSHOTS = ["2010-12-10", "2011-09-01", "2011-12-10"]
KEY_COUNTRIES = {"Netherlands": 1, "Ireland": 2, "Australia": 1}      # how many top accounts per country
EXPECTED_KEY = {"Netherlands": [14646], "Ireland": [14156, 14911], "Australia": [12415]}   # from step 5

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


def tidy(df, nd=1):
    """Round numbers and show missing values as empty cells (for Markdown)."""
    return df.round(nd).astype(object).where(df.notna(), "")


def label(idx):
    return f"{idx // 12}-{idx % 12 + 1:02d}"


# ------------------------------------------------------------------ 1. Load
inv = pd.read_csv(IN / "invoices.csv", dtype={"invoice": str}, low_memory=False)
cust = pd.read_csv(IN / "customers.csv", low_memory=False)
cal = pd.read_csv(IN / "calendar.csv")
inv["invoice_ts"] = pd.to_datetime(inv["invoice_ts"])
inv["customer_id"] = pd.to_numeric(inv["customer_id"], errors="coerce").astype("Int64")
cust["customer_id"] = pd.to_numeric(cust["customer_id"]).astype("Int64")
inv["midx"] = inv["invoice_ts"].dt.year * 12 + inv["invoice_ts"].dt.month - 1     # month index
inv["month"] = inv["invoice_ts"].dt.to_period("M").astype(str)
partial = set(cal.loc[cal["is_partial_month"], "year_month"])
last_complete = int(inv.loc[~inv["month"].isin(partial), "midx"].max())            # last complete month
data_end = inv["invoice_ts"].max().normalize()
base_idx = int(pd.Period(BASE_COHORT).year * 12 + pd.Period(BASE_COHORT).month - 1)

# ------------------------------------------------------------------ 2. Customer table (first order, orders)
oid = inv[(inv["n_sale_lines"] > 0) & inv["customer_id"].notna()].copy()           # identified orders
oid["day"] = oid["invoice_ts"].dt.normalize()
first_idx = oid.groupby("customer_id")["invoice_ts"].idxmin()
fr = oid.loc[first_idx.values]
ct = pd.DataFrame({"first_ts": fr["invoice_ts"].values, "first_day": fr["day"].values,
                   "first_midx": fr["midx"].values, "first_country": fr["country"].values},
                  index=first_idx.index)
ct["n_orders"] = oid.groupby("customer_id")["invoice"].nunique()
ct["is_base"] = ct["first_midx"] == base_idx
ct["market"] = np.where(ct["first_country"] == UK, "UK", "International")

# ------------------------------------------------------------------ 3. Monthly retention matrix
act = oid[["customer_id", "midx"]].drop_duplicates().join(ct["first_midx"], on="customer_id")
act["k"] = act["midx"] - act["first_midx"]
act = act[(act["midx"] <= last_complete) & (act["first_midx"] <= last_complete)]
size = ct[ct["first_midx"] <= last_complete].groupby("first_midx").size()
kmax = last_complete - int(size.index.min())
counts = (act.groupby(["first_midx", "k"])["customer_id"].nunique().unstack(fill_value=0)
          .reindex(index=size.index, columns=range(kmax + 1), fill_value=0))
obs = (size.index.values[:, None] + np.arange(kmax + 1)[None, :]) <= last_complete
mat = (counts.div(size, axis=0) * 100).where(obs)
mat.index = [label(i) + (" (base)" if i == base_idx else "") for i in size.index]
mat.round(2).to_csv(OUT / "05_cohort_retention.csv", index_label="cohort")
n_partial_cohort = int((ct["first_midx"] > last_complete).sum())

new_rows = [i for i in size.index if i != base_idx]


def wavg(rows, ks=range(0, 13)):
    """Size-weighted average monthly retention for the given cohorts (only observable cohorts at each k)."""
    out, nco = {}, {}
    for k in ks:
        ok = [i for i in rows if i + k <= last_complete]
        if ok:
            out[k] = counts.loc[ok, k].sum() / size.loc[ok].sum() * 100
            nco[k] = len(ok)
    return pd.DataFrame({"pct": pd.Series(out), "cohorts": pd.Series(nco)})


ret_new, ret_base = wavg(new_rows), wavg([base_idx])

# ------------------------------------------------------------------ 4. Cumulative net revenue per customer
idn = inv[inv["customer_id"].isin(ct.index)].join(ct["first_midx"], on="customer_id")
net_all = idn["net_product_amount"].sum()                       # for the reconciliation check
idn["k"] = idn["midx"] - idn["first_midx"]
net_before_first = idn.loc[idn["k"] < 0, "net_product_amount"].sum()
idn["k"] = idn["k"].clip(lower=0)                               # returns before the first order go to month 0
idn = idn[(idn["midx"] <= last_complete) & (idn["first_midx"] <= last_complete)]
cum = (idn.groupby(["first_midx", "k"])["net_product_amount"].sum().unstack(fill_value=0)
       .reindex(index=size.index, columns=range(kmax + 1), fill_value=0).cumsum(axis=1))


def wltv(rows, ks=range(0, 13)):
    out, nco = {}, {}
    for k in ks:
        ok = [i for i in rows if i + k <= last_complete]
        if ok:
            out[k] = cum.loc[ok, k].sum() / size.loc[ok].sum()
            nco[k] = len(ok)
    return pd.DataFrame({"gbp": pd.Series(out), "cohorts": pd.Series(nco)})


ltv_new, ltv_base = wltv(new_rows), wltv([base_idx])

# ------------------------------------------------------------------ 5. Repeat rate (later-day order)
od = oid[["customer_id", "day"]].drop_duplicates().join(ct["first_day"], on="customer_id")
second = od[od["day"] > od["first_day"]].groupby("customer_id")["day"].min()
ct["days_to_second"] = (second - ct["first_day"]).dt.days
for w in WINDOWS:
    ct[f"elig_{w}"] = (ct["first_day"] + pd.Timedelta(days=w)) <= data_end
    ct[f"rep_{w}"] = ct["days_to_second"] <= w                  # NaN (no second day) compares as False
ct["cohort_q"] = ct["first_day"].dt.to_period("Q").astype(str)
ct["first_month_no"] = ct["first_day"].dt.month
same_day_only = int(((ct["n_orders"] >= 2) & ct["days_to_second"].isna()).sum())


def rep_rate(df, w):
    e = df[df[f"elig_{w}"]]
    return len(e), (e[f"rep_{w}"].mean() * 100 if len(e) else np.nan)


rep_rows = []
for w in WINDOWS:
    n_new, r_new = rep_rate(ct[~ct["is_base"]], w)
    n_b, r_b = rep_rate(ct[ct["is_base"]], w)
    rep_rows.append({"window_days": w, "new_cohorts_eligible": n_new, "new_cohorts_repeat_pct": r_new,
                     "base_cohort_eligible": n_b, "base_cohort_repeat_pct": r_b})
rep_tbl = pd.DataFrame(rep_rows)

q_rows = []
for q, g_ in ct.groupby("cohort_q"):
    row = {"cohort_quarter": q + ("*" if g_["is_base"].all() else ""), "customers": len(g_)}
    for w in WINDOWS:
        row[f"repeat_{w}d_pct"] = g_[f"rep_{w}"].mean() * 100 if g_[f"elig_{w}"].all() else np.nan
    q_rows.append(row)
q_tbl = pd.DataFrame(q_rows)

grp_rows = []
nb = ct[~ct["is_base"]]
for name, d in (("Acquired Sep-Nov (peak season)", nb[nb["first_month_no"].isin([9, 10, 11])]),
                ("Acquired Dec-Aug", nb[~nb["first_month_no"].isin([9, 10, 11])]),
                ("First order from UK", nb[nb["market"] == "UK"]),
                ("First order from abroad", nb[nb["market"] == "International"])):
    n180, r180 = rep_rate(d, 180)
    n365, r365 = rep_rate(d, 365)
    grp_rows.append({"group (new cohorts)": name, "eligible_180d": n180, "repeat_180d_pct": r180,
                     "eligible_365d": n365, "repeat_365d_pct": r365})
grp_tbl = pd.DataFrame(grp_rows)

# cohort summary (csv + report)
summ = pd.DataFrame({"cohort": mat.index, "customers": size.values})
for k in (1, 2, 3, 6, 9, 12):
    summ[f"M{k}_active_pct"] = mat[k].values if k in mat.columns else np.nan
summ.round(2).to_csv(OUT / "05_cohort_summary.csv", index=False)

# ------------------------------------------------------------------ 6. Open checks from step 5
# A. customer IDs in invoices.csv but not in customers.csv
ex = inv[inv["customer_id"].notna() & ~inv["customer_id"].isin(cust["customer_id"])]
if len(ex):
    a_tbl = ex.groupby("invoice_type").agg(invoices=("invoice", "nunique"), customers=("customer_id", "nunique"),
                                           net_product_amount=("net_product_amount", "sum"),
                                           shipping_amount=("shipping_amount", "sum"),
                                           fee_adjustment_amount=("fee_adjustment_amount", "sum")).round(2).reset_index()
else:
    a_tbl = pd.DataFrame({"invoice_type": ["(none)"]})


# B. RFM at other snapshot dates (same rules as step 5)
def quintile(s):
    return pd.qcut(s.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)


def rfm_at(asof):
    asof = pd.Timestamp(asof)
    sub = inv[inv["invoice_ts"] < asof]
    so = sub[(sub["n_sale_lines"] > 0) & sub["customer_id"].notna()].groupby("customer_id")
    t = pd.DataFrame({"orders": so["invoice"].nunique(), "last": so["invoice_ts"].max()})
    t["net_revenue"] = sub[sub["customer_id"].notna()].groupby("customer_id")["net_product_amount"].sum()
    t["recency_days"] = (asof - t["last"].dt.normalize()).dt.days
    t["R"] = 6 - quintile(t["recency_days"])
    t["F"] = pd.cut(t["orders"], FREQ_BINS, labels=[1, 2, 3, 4, 5]).astype(int)
    t["M"] = quintile(t["net_revenue"])
    R_, F_ = t["R"], t["F"]
    t["segment"] = np.select([(R_ >= 4) & (F_ >= 4), (R_ >= 3) & (F_ >= 3), (R_ >= 4) & (F_ <= 2),
                              (R_ <= 2) & (F_ >= 3), (R_ <= 2) & (F_ <= 2)],
                             ["Champions", "Loyal", "New / Promising", "At Risk", "Hibernating"],
                             default="Needs Attention")
    return t


snap = {a: rfm_at(a) for a in SNAPSHOTS}
b_rows = []
for sname in SEGMENT_ORDER:
    row = {"segment": sname}
    for a, t in snap.items():
        s_ = t[t["segment"] == sname]
        row[f"{a} customers %"] = round(len(s_) / len(t) * 100, 1)
        row[f"{a} net %"] = round(s_["net_revenue"].sum() / t["net_revenue"].sum() * 100, 1)
    b_rows.append(row)
extra = {"segment": "customers scored"}
extra2 = {"segment": "R>=4 means last order within (days)"}
for a, t in snap.items():
    extra[f"{a} customers %"], extra[f"{a} net %"] = f"{len(t):,}", ""
    extra2[f"{a} customers %"], extra2[f"{a} net %"] = int(t.loc[t["R"] == 4, "recency_days"].max()), ""
b_tbl = pd.DataFrame(b_rows + [extra, extra2])
final = snap["2011-12-10"]


# C. International growth with and without the biggest accounts
def per(df):
    return (df.loc[df["month"].between(*P1), "net_product_amount"].sum(),
            df.loc[df["month"].between(*P2), "net_product_amount"].sum())


def chg(a, b):
    return (b / a - 1) * 100 if a else np.nan


def c_row(name, sub, ids):
    t1, t2 = per(sub)
    k1, k2 = per(sub[sub["customer_id"].isin(ids)])
    return {"market": name, "key_accounts": ", ".join(str(int(i)) for i in ids) or "-",
            "total_P1": t1, "total_P2": t2, "total_change_pct": chg(t1, t2),
            "key_P1": k1, "key_P2": k2, "ex_key_P1": t1 - k1, "ex_key_P2": t2 - k2,
            "ex_key_change_pct": chg(t1 - k1, t2 - k2)}


c_rows, key_found, key_all = [], {}, []
for ctry, k in KEY_COUNTRIES.items():
    sub = inv[inv["country"] == ctry]
    ids = sub[sub["customer_id"].notna()].groupby("customer_id")["net_product_amount"].sum().nlargest(k).index.tolist()
    key_found[ctry] = sorted(int(i) for i in ids)
    key_all += ids
    c_rows.append(c_row(ctry, sub, ids))
intl = inv[inv["country"] != UK]
c_rows.append(c_row("International (all)", intl, list(dict.fromkeys(key_all))))
c_tbl = pd.DataFrame(c_rows)

# ------------------------------------------------------------------ 7. Sanity checks
chk = []


def check(name, got, exp, tol=0.01):
    ok = abs(got - exp) <= tol
    chk.append({"Check": name, "Computed": f"{got:,.2f}", "Expected": f"{exp:,.2f}", "Status": "OK" if ok else "DIFF"})


def check_txt(name, got, exp):
    chk.append({"Check": name, "Computed": str(got), "Expected": str(exp), "Status": "OK" if str(got) == str(exp) else "DIFF"})


check("Customers with at least one order", len(ct), 5852)
check("Customers with 2+ orders (5,852 minus 1,618 with F=1 in step 5)", int((ct["n_orders"] >= 2).sum()), 4234)
check("Orders of identified customers", int(ct["n_orders"].sum()), 36594)
check("Net revenue of customers with orders (all months)", net_all, 16413300.86)
check("Replicates step 5 at 2011-12-10: Champions customers", int((final["segment"] == "Champions").sum()), 1389)
check("Replicates step 5 at 2011-12-10: Champions net revenue",
      final.loc[final["segment"] == "Champions", "net_revenue"].sum(), 11412742.46)
check("Replicates step 5 at 2011-12-10: At Risk customers", int((final["segment"] == "At Risk").sum()), 710)
check("International net P1 (step 4)", c_tbl.iloc[-1]["total_P1"], 1269189.62)
check("International net P2 (step 4)", c_tbl.iloc[-1]["total_P2"], 1448937.58)
check_txt("Biggest accounts found (NL / IE / AU) match step 5",
          {k: key_found[k] for k in KEY_COUNTRIES}, EXPECTED_KEY)
checks = pd.DataFrame(chk)

# ------------------------------------------------------------------ 8. Charts
fig, ax = plt.subplots(figsize=(10, 7.5))
cmap = LinearSegmentedColormap.from_list("blues", ["#ffffff", BLUE])
im = ax.imshow(np.ma.masked_invalid(mat.values.astype(float)), cmap=cmap, vmin=0, vmax=HEAT_CAP, aspect="auto")
ax.set_xticks(range(kmax + 1)); ax.set_yticks(range(len(mat))); ax.set_yticklabels(mat.index, fontsize=8)
ax.set_xlabel("Months since first order"); ax.set_ylabel("Cohort (month of first order)")
ax.set_title("Monthly customer retention by cohort")
cb = fig.colorbar(im, ax=ax); cb.set_label(f"Customers active in month (%), color capped at {HEAT_CAP}%")
fig.tight_layout(); fig.savefig(OUT / "05_retention_heatmap.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(7.5, 4.8))
ax.plot(ret_new.index, ret_new["pct"], color=BLUE, marker="o", lw=2, label="New cohorts (2010-01 onward)")
ax.plot(ret_base.index, ret_base["pct"], color=ORANGE, marker="s", lw=2, label="Base cohort 2009-12 (includes existing customers)")
ax.set_xlabel("Months since first order"); ax.set_ylabel("Customers active in month (%)")
ax.set_title("Average monthly retention"); ax.grid(alpha=.3); ax.legend()
fig.tight_layout(); fig.savefig(OUT / "05_retention_curve.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 4.8))
styles = {90: (ORANGE, "-"), 180: (BLUE, "--"), 365: (BLUE, "-")}
for w, (col, ls) in styles.items():
    ax.plot(q_tbl["cohort_quarter"], q_tbl[f"repeat_{w}d_pct"], color=col, ls=ls, marker="o", lw=2, label=f"within {w} days")
ax.set_xlabel("Cohort quarter (first order); * = December 2009 only, includes existing customers")
ax.set_ylabel("Customers with a repeat order (%)")
ax.set_title("Repeat purchase rate by cohort (only fully observable windows)")
ax.grid(alpha=.3); ax.legend(); plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
fig.tight_layout(); fig.savefig(OUT / "05_repeat_rate.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(7.5, 4.8))
ax.plot(ltv_new.index, ltv_new["gbp"], color=BLUE, marker="o", lw=2, label="New cohorts (2010-01 onward)")
ax.plot(ltv_base.index, ltv_base["gbp"], color=ORANGE, marker="s", lw=2, label="Base cohort 2009-12")
ax.set_xlabel("Months since first order"); ax.set_ylabel("Cumulative net revenue per customer (GBP)")
ax.set_title("Cumulative net revenue per acquired customer")
ax.grid(alpha=.3); ax.legend()
fig.tight_layout(); fig.savefig(OUT / "05_cumulative_value.png", dpi=150); plt.close(fig)

# ------------------------------------------------------------------ 9. Report
KS = [1, 2, 3, 6, 9, 12]
avg_t = pd.DataFrame({"months_since_first": KS,
                      "new_cohorts_active_pct": [ret_new["pct"].get(k, np.nan) for k in KS],
                      "new_cohorts_n": [ret_new["cohorts"].get(k, np.nan) for k in KS],
                      "base_active_pct": [ret_base["pct"].get(k, np.nan) for k in KS]})
KL = [0, 1, 3, 6, 9, 12]
ltv_t = pd.DataFrame({"months_since_first": KL,
                      "new_cohorts_gbp": [ltv_new["gbp"].get(k, np.nan) for k in KL],
                      "new_cohorts_n": [ltv_new["cohorts"].get(k, np.nan) for k in KL],
                      "base_gbp": [ltv_base["gbp"].get(k, np.nan) for k in KL]})
c_show = c_tbl.copy()
for col in ("total_P1", "total_P2", "key_P1", "key_P2", "ex_key_P1", "ex_key_P2"):
    c_show[col] = c_show[col].round(0)
for col in ("total_change_pct", "ex_key_change_pct"):
    c_show[col] = c_show[col].map(lambda v: "" if pd.isna(v) else f"{v:+.1f}%")

report = "\n".join([
    "# Step 6 - Cohorts and retention", "",
    "## Sanity checks", md(checks), "",
    f"- Last complete month: {label(last_complete)}; last data day: {data_end.date()}; partial months excluded: {sorted(partial)}",
    f"- Base cohort = {BASE_COHORT} ({int(size.get(base_idx, 0)):,} customers): data starts here, so it includes customers who already existed",
    f"- Customers whose first order is in a partial month (no retention yet): {n_partial_cohort:,}",
    f"- Net revenue booked before a customer's first order month (returns of earlier purchases, put in month 0): {net_before_first:,.2f}", "",
    "## Cohort summary (monthly active %, complete months only)", md(tidy(summ)), "",
    "## Average monthly retention (size-weighted, only cohorts observable at that month)", md(tidy(avg_t)), "",
    "## Repeat purchase: a later-day order within N days (only fully observable customers)", md(tidy(rep_tbl)), "",
    f"- Customers with 2+ invoices but no order on a later day (same-day invoices only): {same_day_only:,}",
    f"- Median days to the second order among new-cohort customers who repeated: {ct.loc[~ct['is_base'], 'days_to_second'].median():.0f}", "",
    "## Repeat rate by cohort quarter (blank = window not fully observable; * = base)", md(tidy(q_tbl)), "",
    "## Repeat rate by how the customer was acquired (new cohorts)", md(tidy(grp_tbl)), "",
    "- Groups differ in which calendar months are observable, so compare them with care.", "",
    "## Cumulative net revenue per acquired customer (GBP)", md(tidy(ltv_t)), "",
    "## Appendix A - customer IDs in invoices.csv but not in customers.csv (open from step 5)", md(a_tbl), "",
    "## Appendix B - RFM segments at other snapshot dates (is Recency flattered by the season?)", md(b_tbl), "",
    "- Same rules as step 5; for each date only orders before that date are used.", "",
    "## Appendix C - international growth with and without the biggest accounts (P1 = Dec09-Nov10, P2 = Dec10-Nov11)",
    md(c_show), "",
    "- Biggest accounts = top customers by net revenue inside each country (invoice country).",
    "- International (all) removes all of those accounts together.", "",
])
(OUT / "05_retention_report.md").write_text(report, encoding="utf-8")
print(f"Done. Files written to: {OUT.resolve()}")
print(checks.to_string(index=False))
