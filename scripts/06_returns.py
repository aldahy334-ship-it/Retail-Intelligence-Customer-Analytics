#!/usr/bin/env python3
"""
06_returns.py - Step 7: Returns and cancellations
Retail Intelligence & Customer Analytics (UCI Online Retail II)

Read-only: reads clean_output/model/*.csv, writes only a report (md) and charts (PNG).
Cancellations cannot be linked to their original invoice (cleaning_log D8), so every
"timing" or "matching" result below is customer + product level, not invoice level.
"""
import argparse
import os

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, ORANGE = "#2f5d8a", "#e08e2b"
D13_SALE = ["581483", "541431"]          # mega-orders (D13)
D13_CANCEL = ["C581484", "C541433"]      # their cancellations
FAMILY = "79323"                         # Cherry Lights family (hypothesis from step 3)


# ---------- helpers ----------
def fmt(v):
    if isinstance(v, (float, np.floating)):
        return "" if pd.isna(v) else f"{v:.2f}"
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    return str(v)


def md(df):
    cols = list(df.columns)
    out = ["| " + " | ".join(str(c) for c in cols) + " |",
           "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(fmt(v) for v in r.values) + " |")
    return "\n".join(out)


def pct(a, b):
    return 100.0 * a / b if b else np.nan


def is_true(s):
    return s.astype(str).str.lower().eq("true")


def main():
    ap = argparse.ArgumentParser(description="Step 7: returns and cancellations (read-only)")
    ap.add_argument("--in", dest="inp", default=os.path.join("clean_output", "model"))
    ap.add_argument("--out", default="analysis_output")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    # ---------- load ----------
    sl = pd.read_csv(
        os.path.join(a.inp, "sales_lines.csv"),
        usecols=["invoice", "stock_code", "quantity", "line_amount", "row_type",
                 "invoice_ts", "customer_id", "country", "is_dotcom_code"],
        dtype={"invoice": str, "stock_code": str}, parse_dates=["invoice_ts"])
    sl["is_dotcom_code"] = is_true(sl["is_dotcom_code"])
    sl["month"] = sl["invoice_ts"].dt.to_period("M").astype(str)
    inv = pd.read_csv(os.path.join(a.inp, "invoices.csv"), usecols=["invoice", "returns_amount"],
                      dtype={"invoice": str})
    cus = pd.read_csv(os.path.join(a.inp, "customers.csv"),
                      usecols=["customer_id", "net_product_amount", "has_orders"])
    prod = pd.read_csv(os.path.join(a.inp, "products.csv"),
                       usecols=["stock_code", "product_description"], dtype={"stock_code": str})
    cal = pd.read_csv(os.path.join(a.inp, "calendar.csv"), usecols=["year_month", "is_partial_month"])
    partial = set(cal.loc[is_true(cal["is_partial_month"]), "year_month"].astype(str))
    desc = prod.set_index("stock_code")["product_description"]

    sale = sl[sl.row_type == "sale"]
    canc = sl[sl.row_type == "cancellation"]
    excl = set(D13_SALE + D13_CANCEL)
    sale_x = sale[~sale.invoice.isin(excl)]      # D13 pairs excluded (net effect is zero)
    canc_x = canc[~canc.invoice.isin(excl)]
    gross_x, ret_x = sale_x.line_amount.sum(), canc_x.line_amount.sum()

    L = ["# Step 7 - Returns and cancellations", ""]

    # ---------- sanity checks ----------
    chk = []

    def check(name, computed, expected, tol=0.01):
        chk.append([name, f"{computed:,.2f}", f"{expected:,.2f}",
                    "OK" if abs(computed - expected) <= tol else "DIFF"])

    check("Gross product sales", sale.line_amount.sum(), 19700954.46)
    check("Returns (cancellation lines)", canc.line_amount.sum(), -719692.94)
    check("Cancellation lines", len(canc), 17974, 0)
    check("Cancellation invoices", canc.invoice.nunique(), 7406, 0)
    check("Cancellation lines with Customer ID (%)", pct(canc.customer_id.notna().sum(), len(canc)), 98.2, 0.1)
    check("D13 cancellations (C581484 + C541433)", canc[canc.invoice.isin(D13_CANCEL)].line_amount.sum(), -245653.20)
    check("Returns excluding D13", ret_x, -474039.74)
    check("Gross excluding D13", gross_x, 19455301.26)
    check("Returns: invoices.csv vs sales_lines", inv.returns_amount.sum(), canc.line_amount.sum())
    # Hypothesis from step 6 (DIFF of 1,406.13): cancel-only customers' net
    co = cus.loc[~is_true(cus["has_orders"]), "net_product_amount"].sum()
    check("Net of cancellation-only customers (explains step 5 vs 6 gap)", co, -1406.13, 0.05)
    L += ["## Sanity checks", md(pd.DataFrame(chk, columns=["Check", "Computed", "Expected", "Status"])), ""]
    L += [f"- Overall return rate excluding D13 pairs: **{pct(-ret_x, gross_x):.2f}%** of gross "
          f"({-ret_x:,.2f} of {gross_x:,.2f})", ""]

    # ---------- monthly trend ----------
    g = sale_x.groupby("month").line_amount.sum().rename("gross")
    r = canc_x.groupby("month").line_amount.sum().rename("returns")
    ci = canc_x.groupby("month").invoice.nunique().rename("cancel_invoices")
    oi = sale_x.groupby("month").invoice.nunique().rename("orders")
    m = pd.concat([g, r, ci, oi], axis=1).fillna(0).reset_index().rename(columns={"index": "month"})
    m["return_rate_pct"] = -m["returns"] / m["gross"] * 100
    m["cancel_inv_per_100_orders"] = m["cancel_invoices"] / m["orders"] * 100
    m["partial"] = np.where(m["month"].isin(partial), "partial", "")
    mc = m[m.partial == ""].copy()

    p1 = mc[(mc.month >= "2009-12") & (mc.month <= "2010-11")]
    p2 = mc[(mc.month >= "2010-12") & (mc.month <= "2011-11")]
    rows = []
    for name, p in [("Dec09-Nov10", p1), ("Dec10-Nov11", p2)]:
        rows.append([name, p.gross.sum(), -p["returns"].sum(),
                     pct(-p["returns"].sum(), p.gross.sum()),
                     p.cancel_invoices.sum(), pct(p.cancel_invoices.sum(), p.orders.sum())])
    L += ["## Returns over time (booked in the month of the cancellation, D13 pairs excluded)",
          md(pd.DataFrame(rows, columns=["period", "gross", "returns_abs", "return_rate_pct",
                                         "cancel_invoices", "cancel_inv_per_100_orders"])), ""]
    peak = mc.month.str[-2:].isin(["09", "10", "11"])
    L += [f"- Sep-Nov months: return rate {pct(-mc[peak]['returns'].sum(), mc[peak].gross.sum()):.2f}% "
          f"vs other months {pct(-mc[~peak]['returns'].sum(), mc[~peak].gross.sum()):.2f}% (complete months)",
          f"- Highest monthly return rate: {mc.loc[mc.return_rate_pct.idxmax(), 'month']} "
          f"({mc.return_rate_pct.max():.2f}%); lowest: {mc.loc[mc.return_rate_pct.idxmin(), 'month']} "
          f"({mc.return_rate_pct.min():.2f}%)",
          f"- Partial months excluded: {sorted(partial)}", "",
          "### Monthly table",
          md(m[["month", "gross", "returns", "return_rate_pct", "cancel_invoices", "orders",
                "cancel_inv_per_100_orders", "partial"]]), ""]

    # ---------- cancellation invoices ----------
    ci_df = canc_x.groupby("invoice").agg(value=("line_amount", lambda s: -s.sum()),
                                          lines=("line_amount", "size"),
                                          customer_id=("customer_id", "first")).reset_index()
    tot_inv = ci_df.value.sum()
    top10 = ci_df.value.nlargest(10).sum()
    L += ["## Size of cancellation invoices (D13 excluded)",
          md(pd.DataFrame([["Cancellation invoices", len(ci_df)],
                           ["Median value", ci_df.value.median()],
                           ["Mean value", ci_df.value.mean()],
                           ["90th percentile value", ci_df.value.quantile(0.9)],
                           ["Median lines per invoice", ci_df.lines.median()],
                           ["Share of invoices under 50 (%)", pct((ci_df.value < 50).sum(), len(ci_df))],
                           ["Top 10 invoices, share of returned value (%)", pct(top10, tot_inv)]],
                          columns=["metric", "value"])), ""]

    # ---------- customers ----------
    idc = canc_x[canc_x.customer_id.notna()]
    rc = (-idc.groupby("customer_id").line_amount.sum()).sort_values(ascending=False)
    n, tot = len(rc), rc.sum()
    rows = []
    for lab, f in [("Top 1%", .01), ("Top 5%", .05), ("Top 10%", .10), ("Top 20%", .20)]:
        k = max(1, int(round(n * f)))
        rows.append([lab, k, rc.iloc[:k].sum(), pct(rc.iloc[:k].sum(), tot)])
    k50 = int((rc.cumsum() / tot >= 0.5).values.argmax()) + 1
    n_buyers = sale.customer_id.nunique()
    gc = sale_x.groupby("customer_id").line_amount.sum()
    cust_rate = (rc / gc.reindex(rc.index)).replace([np.inf, -np.inf], np.nan).dropna() * 100
    L += ["## Who returns: customers (identified customers with a cancellation)",
          f"- Customers with at least one cancellation: **{n:,}** = {pct(n, n_buyers):.1f}% of {n_buyers:,} buyers",
          f"- 50% of identified returned value comes from **{k50}** customers ({pct(k50, n):.1f}% of returners)",
          f"- Median customer return rate (returned / own gross): {cust_rate.median():.1f}%",
          md(pd.DataFrame(rows, columns=["group", "customers", "returned_value", "share_of_identified_returns_pct"])), ""]
    t = rc.head(10).reset_index().rename(columns={"line_amount": "returned_value"})
    t.columns = ["customer_id", "returned_value"]
    t["customer_id"] = t.customer_id.astype("int64")
    t["country"] = t.customer_id.map(canc_x.dropna(subset=["customer_id"]).assign(
        c=lambda d: d.customer_id.astype("int64")).groupby("c").country.last())
    t["gross"] = t.customer_id.map(gc.rename(index=lambda x: int(x) if pd.notna(x) else x))
    t["return_rate_pct"] = t.returned_value / t.gross * 100
    t["cancel_invoices"] = t.customer_id.map(idc.assign(c=idc.customer_id.astype("int64")).groupby("c").invoice.nunique())
    L += ["### Top 10 customers by returned value", md(t), ""]

    anon = canc_x[canc_x.customer_id.isna()]
    L += ["## Anonymous cancellations (no Customer ID)",
          f"- {len(anon):,} lines, {anon.invoice.nunique():,} invoices, returned value {-anon.line_amount.sum():,.2f} "
          f"= {pct(anon.line_amount.sum(), ret_x):.1f}% of returns", ""]

    # ---------- markets ----------
    rows = []
    for lab, f in [("UK", lambda d: d.country == "United Kingdom"), ("International", lambda d: d.country != "United Kingdom")]:
        gg, rr = sale_x[f(sale_x)].line_amount.sum(), canc_x[f(canc_x)].line_amount.sum()
        rows.append([lab, gg, -rr, pct(-rr, gg)])
    L += ["## UK vs International", md(pd.DataFrame(rows, columns=["market", "gross", "returns_abs", "return_rate_pct"])), ""]

    # ---------- products ----------
    pv = (-canc_x.groupby("stock_code").line_amount.sum()).sort_values(ascending=False)
    k50p = int((pv.cumsum() / pv.sum() >= 0.5).values.argmax()) + 1
    L += ["## Concentration of returned value by product",
          f"- Products with any return: {len(pv):,}; top 10 = {pct(pv.head(10).sum(), pv.sum()):.1f}%, "
          f"top 100 = {pct(pv.head(100).sum(), pv.sum()):.1f}% of returned value",
          f"- 50% of returned value comes from {k50p} products", ""]

    # ---------- customer-product matching ----------
    cs = sale_x[sale_x.customer_id.notna()].copy()
    cs["cid"] = cs.customer_id.astype("int64")
    bought = cs.groupby(["cid", "stock_code"]).quantity.sum().rename("units_bought").reset_index()
    cr = canc_x[canc_x.customer_id.notna()].copy()
    cr["cid"] = cr.customer_id.astype("int64")
    cr["ret_value"] = -cr.line_amount
    cr = cr.merge(bought, on=["cid", "stock_code"], how="left")
    cr["never_bought"] = cr.units_bought.isna()
    cr["fam"] = cr.stock_code.str.startswith(FAMILY)
    fam_buyers = set(cs.loc[cs.stock_code.str.startswith(FAMILY), "cid"].unique())
    cr["bought_other_family_code"] = cr.fam & cr.never_bought & cr.cid.isin(fam_buyers)
    cr["never_bought_any_family"] = cr.fam & ~cr.cid.isin(fam_buyers)

    def orphan_row(lab, d):
        v = d.ret_value.sum()
        return [lab, len(d), v, pct(d.loc[d.never_bought, "ret_value"].sum(), v)]

    L += ["## Customer-product matching (no invoice link, so this is a customer-level test)",
          "A return line is an 'orphan' when that customer has no purchase of that product code anywhere in the data. "
          "Purchases before 2009-12 are invisible, so some orphans are expected.",
          md(pd.DataFrame([orphan_row("All products", cr), orphan_row("Family 79323*", cr[cr.fam]),
                           orphan_row("All other products", cr[~cr.fam])],
                          columns=["group", "return_lines", "returned_value", "orphan_value_pct"])), ""]

    # days from the customer's latest earlier purchase of the same product to the return
    pur = cs[["cid", "stock_code", "invoice_ts"]].rename(columns={"invoice_ts": "pts"}).sort_values("pts")
    ret = cr[["cid", "stock_code", "invoice_ts"]].sort_values("invoice_ts")
    mm = pd.merge_asof(ret, pur, left_on="invoice_ts", right_on="pts", by=["cid", "stock_code"], direction="backward")
    days = ((mm.invoice_ts - mm.pts).dt.total_seconds() / 86400).dropna()
    L += ["## Time from the customer's latest earlier purchase of the same product to the return",
          f"- Return lines with an earlier purchase of that product by that customer: {len(days):,} of {len(mm):,} "
          f"({pct(len(days), len(mm)):.1f}%)"]
    if len(days):
        L += [f"- Median {days.median():.0f} days; 75th percentile {days.quantile(.75):.0f}; 90th percentile {days.quantile(.9):.0f}",
              f"- Within 30 days: {pct((days <= 30).sum(), len(days)):.1f}%; within 90 days: {pct((days <= 90).sum(), len(days)):.1f}%"]
    L += ["- Caveat: this is the latest earlier purchase, not necessarily the one being returned.", ""]

    # ---------- family 79323* ----------
    pg = sale_x[~sale_x.is_dotcom_code].groupby("stock_code").agg(gross=("line_amount", "sum"),
                                                                  orders=("invoice", "nunique"))
    prr = canc_x.groupby("stock_code").agg(returns=("line_amount", "sum"), cancel_invoices=("invoice", "nunique"))
    p = pg.join(prr, how="left").fillna(0)
    p["return_rate_pct"] = -p["returns"] / p["gross"] * 100

    fam_codes = sorted(c for c in p.index if c.startswith(FAMILY))
    rows = []
    for c in fam_codes:
        d = cr[cr.stock_code == c]
        v = d.ret_value.sum()
        rows.append([c, desc.get(c, ""), p.loc[c, "gross"], -p.loc[c, "returns"], p.loc[c, "return_rate_pct"],
                     int(p.loc[c, "orders"]), d.cid.nunique(),
                     pct(d.loc[d.never_bought, "ret_value"].sum(), v),
                     pct(d.loc[d.bought_other_family_code, "ret_value"].sum(), v)])
    fam_tab = pd.DataFrame(rows, columns=["stock_code", "description", "gross", "returns_abs", "return_rate_pct",
                                          "sale_orders", "return_customers", "orphan_value_pct",
                                          "other_color_bought_pct"])
    fg, fr = p.loc[fam_codes, "gross"].sum(), -p.loc[fam_codes, "returns"].sum()
    fd = cr[cr.fam]
    L += ["## Family 79323* (Cherry Lights): is the high return rate a coding artefact?",
          "Hypothesis from step 3: either real defects, or colours entered under the wrong code. "
          "Test: for returned value of one colour, how often did the same customer buy a DIFFERENT 79323* colour "
          "but never this one (other_color_bought_pct)?",
          f"- Family combined: gross {fg:,.2f}, returns {fr:,.2f}, return rate {pct(fr, fg):.2f}% "
          f"(store-wide {pct(-ret_x, gross_x):.2f}%)",
          f"- Family returned value where the customer never bought ANY 79323* code: "
          f"{pct(fd.loc[fd.never_bought_any_family, 'ret_value'].sum(), fd.ret_value.sum()):.1f}% "
          f"(vs {pct(fd.loc[fd.never_bought, 'ret_value'].sum(), fd.ret_value.sum()):.1f}% at single-code level)",
          md(fam_tab), ""]

    # ---------- other high-rate products ----------
    q = p[(p.orders >= 50) & (p.gross > 0) & (~p.index.str.startswith(FAMILY))].sort_values("return_rate_pct", ascending=False).head(10)
    rows = []
    for c, rw in q.iterrows():
        d = cr[cr.stock_code == c]
        byc = d.groupby("cid").ret_value.sum().sort_values(ascending=False)
        rows.append([c, desc.get(c, ""), rw.gross, -rw["returns"], rw.return_rate_pct, int(rw.orders),
                     len(byc), pct(byc.iloc[0], byc.sum()) if len(byc) else np.nan,
                     pct(d.loc[d.never_bought, "ret_value"].sum(), d.ret_value.sum())])
    L += ["## Highest return rates outside the 79323* family (products with >= 50 orders)",
          "- top_customer_pct: share of this product's identified returned value from its single biggest returner.",
          md(pd.DataFrame(rows, columns=["stock_code", "description", "gross", "returns_abs", "return_rate_pct",
                                         "orders", "return_customers", "top_customer_pct", "orphan_value_pct"])), ""]

    # ---------- charts ----------
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(mc.month, -mc["returns"], color=BLUE)
    ax.set_ylabel("Returned value (GBP)")
    ax.set_title("Returns by month (complete months, D13 pairs excluded)")
    ax.tick_params(axis="x", rotation=90)
    ax2 = ax.twinx()
    ax2.plot(mc.month, mc.return_rate_pct, color=ORANGE, marker="o")
    ax2.set_ylabel("Return rate (% of gross)")
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "06_returns_monthly.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    x = np.arange(1, n + 1) / n * 100
    ax.plot(x, rc.cumsum().values / tot * 100, color=BLUE)
    ax.plot([0, 100], [0, 100], color=ORANGE, linestyle="--")
    ax.set_xlabel("Customers with returns, ranked (%)")
    ax.set_ylabel("Cumulative share of returned value (%)")
    ax.set_title("Concentration of returned value by customer")
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "06_returns_concentration.png"), dpi=150)
    plt.close(fig)

    if len(fam_tab):
        fig, ax = plt.subplots(figsize=(10, 5))
        xs = np.arange(len(fam_tab))
        ax.bar(xs - 0.2, fam_tab.return_rate_pct, 0.4, color=BLUE, label="Return rate (% of gross)")
        ax.bar(xs + 0.2, fam_tab.other_color_bought_pct.fillna(0), 0.4, color=ORANGE,
               label="Returned value where customer bought another colour (%)")
        ax.set_xticks(xs)
        ax.set_xticklabels(fam_tab.stock_code, rotation=45, ha="right")
        ax.set_title("Cherry Lights (79323*): return rate and colour-mismatch signal")
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(a.out, "06_family_79323.png"), dpi=150)
        plt.close(fig)

    path = os.path.join(a.out, "06_returns_report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"Wrote {path} and 3 charts in {a.out}")


if __name__ == "__main__":
    main()
