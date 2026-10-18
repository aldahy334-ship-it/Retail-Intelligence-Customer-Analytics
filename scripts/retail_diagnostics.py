#!/usr/bin/env python3
"""
retail_diagnostics.py - READ-ONLY follow-up diagnostics for Online Retail II.

Runs six checks and writes one compact report. Nothing is cleaned, deleted
or saved back: the workbook is only read, and all derived columns live in
memory. Source size + mtime are verified at the end.

Usage:
    python retail_diagnostics.py online_retail_II.xlsx
    python retail_diagnostics.py online_retail_II.xlsx --out audit_output --max-rows 25

Output: <out>/diagnostics_report.md  (share this with the assistant)

Checks
  1. Shared invoices: identical line sets across the two sheets?
  2. All non-product / rare-shape stock codes
  3. Negative-price rows and A-prefixed invoices
  4. Non-C negative quantities: is Price always 0?
  5. Zero-price rows that still carry a Customer ID
  6. Where do exact duplicate rows occur (clustering, adjacency, impact)?

Memory note: both sheets are held in one DataFrame (~2x the earlier audit's
single-sheet peak). Close other heavy programs if RAM is tight.
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# Column names exactly as reported by the audit; edit here if yours differ.
INV, STK, DESC, QTY, DATE, PRICE, CUST, CTRY = (
    "Invoice", "StockCode", "Description", "Quantity",
    "InvoiceDate", "Price", "Customer ID", "Country")
RAW_COLS = [INV, STK, DESC, QTY, DATE, PRICE, CUST, CTRY]


def load(path):
    xl = pd.ExcelFile(path)
    names, frames = xl.sheet_names, []
    for i, n in enumerate(names):
        print(f"Reading sheet: {n} ...")
        df = pd.read_excel(xl, sheet_name=n)[RAW_COLS].copy()
        df["_sheet"] = i
        df["_pos"] = np.arange(len(df))  # original row order within sheet
        frames.append(df)
    d = pd.concat(frames, ignore_index=True)
    del frames
    return names, d


def prepare(d):
    """Derived, in-memory-only helper columns. Raw columns stay untouched."""
    d["inv"] = d[INV].astype(str).str.strip()
    d["stk"] = d[STK].astype(str).str.strip()
    d["is_c"] = d.inv.str.upper().str.startswith("C")
    d["qty"] = pd.to_numeric(d[QTY], errors="coerce")
    d["price"] = pd.to_numeric(d[PRICE], errors="coerce")
    d["val"] = d.qty * d.price
    d["has_cust"] = d[CUST].notna()
    d["date"] = pd.to_datetime(d[DATE], errors="coerce")
    d["month"] = d.date.dt.to_period("M").astype(str)
    d["row_hash"] = pd.util.hash_pandas_object(
        d[RAW_COLS].astype(str), index=False).values
    shape = (d.stk.str.replace(r"[A-Za-z]", "A", regex=True)
                  .str.replace(r"\d", "9", regex=True))
    share = shape.value_counts(normalize=True)
    dom = set(share[share >= 0.01].index)  # dominant shapes (>=1% of rows)
    d["shape"] = shape
    d["nonstd"] = ~shape.isin(dom)
    return d, sorted(dom)


def dtxt(s):
    """Description as clean text; missing values become '<missing>'.
    (Newer pandas keeps NaN when calling astype(str), so be explicit.)"""
    return s.astype("string").str.strip().fillna("<missing>").astype(object)


def make_writers(lines, max_rows):
    def w(s=""):
        lines.append(str(s))
        print(s)

    def H(t):
        w()
        w(f"## {t}")

    def T(df, n=None):
        n = n or max_rows
        w("```")
        w(df.head(n).to_string(index=False, max_colwidth=42)
          if len(df) else "(none)")
        if len(df) > n:
            w(f"... {len(df) - n} more rows not shown")
        w("```")
    return w, H, T


# ---------------------------------------------------------------- check 1
def check1(d, names, w, H, T):
    H("1. Shared invoices across sheets")
    A, B = d[d._sheet == 0], d[d._sheet == 1]
    shared = set(A.inv) & set(B.inv)
    w(f"- sheets: A=`{names[0]}`, B=`{names[1]}`")
    w(f"- invoices: A={A.inv.nunique():,} B={B.inv.nunique():,} "
      f"shared={len(shared):,}")
    if not shared:
        w("- no invoice appears in both sheets; skipping line-set comparison")
        return shared, pd.DataFrame({"a": [], "b": []})
    S = d[d.inv.isin(shared)]
    w(f"- rows inside shared invoices: A={int((S._sheet == 0).sum()):,} "
      f"B={int((S._sheet == 1).sum()):,}")
    w(f"- date span of shared-invoice rows: {S.date.min()} -> {S.date.max()}")

    cnt = (S.groupby(["inv", "row_hash", "_sheet"]).size()
             .unstack("_sheet", fill_value=0).reindex(columns=[0, 1], fill_value=0))
    cnt.columns = ["a", "b"]
    cnt["only_a"] = (cnt.a - cnt.b).clip(lower=0)
    cnt["only_b"] = (cnt.b - cnt.a).clip(lower=0)
    per = cnt.groupby("inv")[["a", "b", "only_a", "only_b"]].sum()
    per["status"] = np.select(
        [(per.only_a == 0) & (per.only_b == 0),
         (per.only_a == 0) & (per.only_b > 0),
         (per.only_a > 0) & (per.only_b == 0)],
        ["identical", "A_lines_all_in_B (B has extra)",
         "B_lines_all_in_A (A has extra)"], "differs_both_ways")
    w("- line-set comparison (full-row multiset, duplicates counted):")
    T(per.status.value_counts().rename_axis("status").reset_index(name="invoices"))
    w(f"- lines only in A: {int(per.only_a.sum()):,} | only in B: {int(per.only_b.sum()):,}")

    hdr = (S.groupby(["inv", "_sheet"])
             .agg(dmin=("date", "min"), dmax=("date", "max"),
                  cust=(CUST, "max"), ctry=(CTRY, "first")).unstack("_sheet"))
    w("- invoice-level header mismatches between sheets: "
      f"earliest timestamp={int((hdr[('dmin', 0)] != hdr[('dmin', 1)]).sum())}, "
      f"latest timestamp={int((hdr[('dmax', 0)] != hdr[('dmax', 1)]).sum())}, "
      f"customer={int((hdr[('cust', 0)].fillna(-1) != hdr[('cust', 1)].fillna(-1)).sum())}, "
      f"country={int((hdr[('ctry', 0)] != hdr[('ctry', 1)]).sum())}")

    bad = per.index[per.status != "identical"]
    if len(bad):
        imb = cnt[(cnt.only_a > 0) | (cnt.only_b > 0)].index
        key = pd.MultiIndex.from_frame(S[["inv", "row_hash"]])
        ex = S[key.isin(imb) & S.inv.isin(bad[:5])]
        w("- sample of unmatched lines (first 5 non-identical invoices; "
          "`_sheet` 0=A, 1=B):")
        T(ex[["inv", "stk", "qty", "price", "date", CUST, "_sheet"]]
          .sort_values(["inv", "stk", "_sheet"]), 30)

    lo, hi = max(A.date.min(), B.date.min()), min(A.date.max(), B.date.max())
    w(f"- overlap window by date: {lo} -> {hi}")
    for lab, X, other in (("A", A, B), ("B", B, A)):
        W = X[(X.date >= lo) & (X.date <= hi)]
        in_other = W.inv.isin(set(other.inv))
        w(f"- sheet {lab} rows in window: {len(W):,} "
          f"(distinct full rows {W.row_hash.nunique():,}); "
          f"invoice also in other sheet: {int(in_other.sum()):,}; "
          f"invoice NOT in other sheet: {int((~in_other).sum()):,} "
          f"({W.loc[~in_other, 'inv'].nunique():,} invoices)")
    return shared, cnt


# ---------------------------------------------------------------- check 2
def check2(d, dom, w, H, T):
    H("2. Non-product / rare-shape stock codes")
    w(f"- dominant code shapes (>=1% of all rows; 9=digit, A=letter): `{dom}`")
    c = d[d.nonstd]
    w(f"- rows with a non-dominant shape: {len(c):,} across "
      f"{c.stk.nunique():,} distinct raw codes")
    g = c.groupby("stk").agg(
        rows=("inv", "size"), invoices=("inv", "nunique"),
        n_desc=(DESC, "nunique"), qty_sum=("qty", "sum"), val_sum=("val", "sum"),
        price_min=("price", "min"), price_med=("price", "median"),
        price_max=("price", "max"), pct_cust=("has_cust", "mean"),
        pct_C=("is_c", "mean"),
        sheets=("_sheet", lambda s: "".join(sorted(map(str, set(s))))))
    top = (c.assign(dd=dtxt(c[DESC]))
             .groupby("stk")["dd"]
             .agg(lambda s: s.mode().iloc[0] if len(s.mode()) else "<missing>"))
    g["top_description"] = top
    g = g.sort_values("rows", ascending=False).reset_index()
    for col in ("pct_cust", "pct_C"):
        g[col] = (g[col] * 100).round(0)
    g = g.round(2)
    w("- ALL non-dominant-shape codes (sheets: 0=A only, 1=B only, 01=both):")
    T(g, 500)
    w("- NOTE: shape alone is not a product test; some codes here may be real "
      "products (decide from description, price and customer columns).")

    dm = d[~d.nonstd]
    h = dm.groupby("stk").agg(rows=("inv", "size"),
                              zero_price=("price", lambda s: (s == 0).mean()),
                              desc_missing=(DESC, lambda s: s.isna().mean()))
    h = h[(h.rows >= 10) & ((h.zero_price >= .5) | (h.desc_missing >= .5))]
    w(f"- dominant-shape codes with >=10 rows where >=50% are zero-price or "
      f"description-missing: {len(h)}")
    T(h.sort_values("rows", ascending=False).round(2).reset_index(), 30)


# ---------------------------------------------------------------- check 3
def check3(d, w, H, T):
    H("3. Negative prices and A-prefixed invoices")
    cols = ["_sheet", "inv", STK, DESC, QTY, PRICE, CUST, CTRY, DATE]
    neg = d[d.price < 0]
    w(f"- negative-price rows: {len(neg)}")
    T(neg[cols], 50)
    pre = d.inv.str.extract(r"^([A-Za-z]+)")[0]
    odd = d[pre.notna() & (pre.str.upper() != "C")]
    w(f"- rows on invoices with a non-C letter prefix: {len(odd)} "
      f"({odd.inv.nunique()} invoices; prefixes {sorted(set(pre.dropna()) - {'C'})})")
    T(odd[cols], 50)
    both = set(neg.inv) & set(odd.inv)
    w(f"- invoices that are BOTH negative-price and non-C-prefixed: {len(both)}")
    if len(odd):
        full = d[d.inv.isin(set(odd.inv))]
        w(f"- total lines on those prefixed invoices: {len(full)} "
          f"(extra lines beyond the prefixed rows: {len(full) - len(odd)})")


# ---------------------------------------------------------------- check 4
def check4(d, w, H, T):
    H("4. Non-C negative quantities: is Price always 0?")
    n = d[(~d.is_c) & (d.qty < 0)].copy()
    n["price_class"] = np.select([n.price == 0, n.price > 0, n.price < 0],
                                 ["zero", "positive", "negative"], "nan")
    w(f"- non-C rows with Quantity < 0: {len(n):,}")
    T(pd.crosstab(n._sheet, n.price_class).reset_index())
    w(f"- with a Customer ID: {int(n.has_cust.sum()):,}")
    w(f"- non-C negative rows with Price > 0: {int((n.price > 0).sum())}")
    T(n[n.price > 0][["_sheet", "inv", STK, DESC, QTY, PRICE, CUST, DATE]], 20)
    c = d[d.is_c]
    w(f"- reverse check: C-prefix rows with Price == 0: {int((c.price == 0).sum())}; "
      f"C-prefix rows with Quantity > 0: {int((c.qty > 0).sum())}")
    T(c[c.qty > 0][["_sheet", "inv", STK, DESC, QTY, PRICE, CUST, DATE]], 10)
    dd = (n.assign(dd=dtxt(n[DESC]))["dd"]
            .value_counts().head(15).rename_axis("description").reset_index(name="rows"))
    w("- top descriptions on non-C negative rows:")
    T(dd)


# ---------------------------------------------------------------- check 5
def check5(d, w, H, T):
    H("5. Zero-price rows that still have a Customer ID")
    z = d[(d.price == 0)]
    zc, zn = z[z.has_cust], z[~z.has_cust]
    w(f"- zero-price rows: {len(z):,} | with customer: {len(zc):,} | "
      f"without: {len(zn):,}")
    w("- with customer, by sheet / sign of quantity / C-prefix / non-dominant code:")
    T(pd.DataFrame({
        "sheet": zc._sheet, "qty_sign": np.sign(zc.qty), "is_C": zc.is_c,
        "nonstd_code": zc.nonstd}).value_counts().rename("rows").reset_index())
    w(f"- description missing: with-customer={zc[DESC].isna().mean():.1%} "
      f"vs without-customer={zn[DESC].isna().mean():.1%}")
    w(f"- distinct customers: {zc[CUST].nunique()} (top by rows below)")
    T(zc[CUST].value_counts().head(10).rename_axis("customer").reset_index(name="rows"))
    ctx = (d[d.inv.isin(set(zc.inv))].groupby("inv")
             .agg(lines=("price", "size"), zero_lines=("price", lambda s: (s == 0).sum())))
    ctx["kind"] = np.where(ctx.lines == ctx.zero_lines, "all lines zero-price",
                           "zero-price lines on an otherwise priced invoice")
    w(f"- invoices containing them: {len(ctx):,}")
    T(ctx.kind.value_counts().rename_axis("invoice_kind").reset_index(name="invoices"))
    dd = (zc.assign(dd=dtxt(zc[DESC]))["dd"]
            .value_counts().head(20).rename_axis("description").reset_index(name="rows"))
    w("- top descriptions (with customer):")
    T(dd, 20)
    w("- sample rows:")
    T(zc[["_sheet", "inv", STK, DESC, QTY, PRICE, CUST, CTRY, DATE]]
      .sample(min(15, len(zc)), random_state=0) if len(zc) else zc)


# ---------------------------------------------------------------- check 6
def check6(d, shared, cnt, w, H, T):
    H("6. Exact duplicate rows within sheets")
    g = ["_sheet", "row_hash"]
    extra = d.duplicated(subset=g, keep="first")
    d["_gsize"] = d.groupby(g)["_pos"].transform("size")
    dup_all = d._gsize > 1
    gs = d[dup_all].groupby(g).size()
    w(f"- extra (removable) rows: {int(extra.sum()):,} "
      f"(by sheet: {extra.groupby(d._sheet).sum().to_dict()}); "
      f"duplicated groups: {len(gs):,}")
    w("- group size distribution (rows per identical group):")
    T(gs.clip(upper=5).value_counts().sort_index()
        .rename_axis("group_size(5=5+)").reset_index(name="groups"))

    per = d.groupby(["_sheet", "inv"]).agg(
        lines=("_pos", "size"), min_g=("_gsize", "min"),
        dates=("date", "min"), has_cust=("has_cust", "max"), is_c=("is_c", "max"))
    per["extra"] = d[extra].groupby(["_sheet", "inv"]).size().reindex(per.index, fill_value=0)
    aff = per[per.extra > 0]
    w(f"- invoices with >=1 duplicate: {len(aff):,} of {len(per):,} "
      f"({len(aff) / len(per):.1%})")
    w(f"- invoices where EVERY line is duplicated: "
      f"{int((per.min_g >= 2).sum()):,}")
    frac = (aff.extra / aff.lines)
    T(pd.cut(frac, [0, .05, .1, .25, .5, 1.0], include_lowest=False)
        .value_counts().sort_index().rename_axis("extra_rows/lines").reset_index(name="invoices"))
    srt = aff.extra.sort_values(ascending=False)
    w(f"- concentration: top 10 invoices hold {srt.head(10).sum() / srt.sum():.1%} "
      f"of extra rows; top 10% of affected invoices hold "
      f"{srt.head(max(1, len(srt) // 10)).sum() / srt.sum():.1%}")
    T(aff.sort_values("extra", ascending=False).head(10).reset_index())

    dd = d.loc[dup_all, ["_sheet", "row_hash", "_pos"]].sort_values(g + ["_pos"])
    gap = dd.groupby(g)["_pos"].diff().dropna()
    w(f"- adjacency of repeated rows in file order: gap==1 {np.mean(gap == 1):.1%}, "
      f"<=5 {np.mean(gap <= 5):.1%}, <=50 {np.mean(gap <= 50):.1%}, "
      f"median gap {gap.median():.0f}")

    w("- profile: duplicate-extra rows vs all rows (share):")
    ex = d[extra]
    prof = pd.DataFrame({
        "metric": ["C-prefix", "no Customer ID", "Price == 0", "non-dominant code",
                   "Quantity == 1", "Quantity < 0"],
        "extra_rows": [ex.is_c.mean(), (~ex.has_cust).mean(), (ex.price == 0).mean(),
                       ex.nonstd.mean(), (ex.qty == 1).mean(), (ex.qty < 0).mean()],
        "all_rows": [d.is_c.mean(), (~d.has_cust).mean(), (d.price == 0).mean(),
                     d.nonstd.mean(), (d.qty == 1).mean(), (d.qty < 0).mean()]}).round(4)
    T(prof)
    rate = (ex.groupby(["_sheet", "month"]).size()
              / d.groupby(["_sheet", "month"]).size()).dropna().round(4)
    w("- duplicate-extra rate by sheet/month (extra rows / rows):")
    T(rate.rename("rate").reset_index(), 30)

    pos = d.loc[extra & ~d.is_c & (d.price > 0) & (d.qty > 0), "val"].sum()
    allpos = d.loc[~d.is_c & (d.price > 0) & (d.qty > 0), "val"].sum()
    w(f"- value impact (Quantity*Price) of extra rows: net={ex.val.sum():,.2f}; "
      f"on normal sale rows={pos:,.2f} = {pos / allpos:.2%} of normal-sale value "
      f"(pre-overlap-resolution, descriptive only)")

    rep = d[d.duplicated(["_sheet", "inv", "stk"], keep=False)]
    r = rep.groupby(["_sheet", "inv", "stk"]).agg(
        n=("row_hash", "size"), nh=("row_hash", "nunique"),
        nq=("qty", "nunique"), np_=("price", "nunique"))
    ne = r[r.nh > 1]
    kind = np.select([(ne.nq > 1) & (ne.np_ > 1), ne.nq > 1, ne.np_ > 1],
                     ["qty+price differ", "qty differs", "price differs"],
                     "other (desc/date/customer differ)")
    w(f"- repeated (sheet,invoice,stock) groups: {len(r):,}; all-identical: "
      f"{int((r.nh == 1).sum()):,}; contain different lines: {len(ne):,}")
    T(pd.Series(kind).value_counts().rename_axis("how_lines_differ").reset_index(name="groups"))

    ex_sh = ex[ex.inv.isin(shared)]
    w(f"- extra rows inside the shared (cross-sheet) invoices: {len(ex_sh):,}")
    dc = cnt[(cnt.a > 1) | (cnt.b > 1)]
    if len(dc):
        w(f"- shared-invoice lines duplicated in at least one sheet: {len(dc):,}; "
          f"same multiplicity in both sheets: {int((dc.a == dc.b).sum()):,} "
          f"({(dc.a == dc.b).mean():.1%})")
    d.drop(columns="_gsize", inplace=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--out", default="audit_output")
    ap.add_argument("--max-rows", type=int, default=20)
    a = ap.parse_args()

    src = Path(a.path).resolve()
    st0 = src.stat()
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    t0, lines = time.time(), []
    w, H, T = make_writers(lines, a.max_rows)

    names, d = load(src)
    if len(names) != 2:
        sys.exit(f"Expected 2 sheets, found {names}")
    d, dom = prepare(d)
    w(f"# Retail diagnostics ({src.name})")
    w(f"rows loaded: {len(d):,} | sheets: {names}")

    shared, cnt = check1(d, names, w, H, T)
    check2(d, dom, w, H, T)
    check3(d, w, H, T)
    check4(d, w, H, T)
    check5(d, w, H, T)
    check6(d, shared, cnt, w, H, T)

    st1 = src.stat()
    ok = st0.st_size == st1.st_size and st0.st_mtime == st1.st_mtime
    w()
    w(f"_runtime {time.time() - t0:.0f}s | source file unchanged: **{ok}**_")
    p = out_dir / "diagnostics_report.md"
    p.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {p} ({p.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
