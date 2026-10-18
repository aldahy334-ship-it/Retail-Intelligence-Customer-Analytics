#!/usr/bin/env python3
"""
data_audit.py - Local, read-only data-audit workflow for retail transaction data.

Usage:
    python data_audit.py path/to/online_retail_II.xlsx
    python data_audit.py data.csv --out audit_output --top-k 15
    python data_audit.py data.xlsx --map invoice="Invoice" customer="Customer ID"
    python data_audit.py data.xlsx --no-samples      # omit raw example rows

Outputs (in --out folder, never next to / over the source file):
    audit_report.md    <- compact, share THIS with the AI assistant
    audit_report.json  <- same content, machine-readable

Design rules:
    * Source file is opened read-only; size + mtime are verified afterwards.
    * One sheet in memory at a time; only light artifacts (hashes, ID sets) kept.
    * Column roles are INFERRED from names; nothing is assumed about values.
      Check the "Detected roles" section and override with --map if wrong.
    * Descriptive only: no cleaning, no analysis, no business conclusions.
"""
import argparse
import gc
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

MAX_STR = 60  # truncate long strings in the report

# role -> name hints, in priority order (exact match pass, then substring pass)
ROLE_HINTS = [
    ("date", ["invoicedate", "date", "datetime", "timestamp"]),
    ("invoice", ["invoiceno", "invoice", "orderid", "order"]),
    ("stock", ["stockcode", "sku", "productcode", "itemcode"]),
    ("description", ["description", "productname", "itemname"]),
    ("quantity", ["quantity", "qty"]),
    ("price", ["unitprice", "price"]),
    ("customer", ["customerid", "customer", "clientid"]),
    ("country", ["country"]),
]


# ----------------------------------------------------------------- helpers
def norm(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def detect_roles(columns, overrides):
    roles, used = dict(overrides), set(overrides.values())
    for exact in (True, False):
        for role, hints in ROLE_HINTS:
            if role in roles:
                continue
            for hint in hints:
                hit = [c for c in columns if c not in used
                       and (norm(c) == hint if exact else hint in norm(c))]
                if hit:
                    roles[role] = hit[0]
                    used.add(hit[0])
                    break
    return {r: c for r, c in roles.items() if c in columns}


def clean(o):
    """Make any structure JSON-safe, rounded and truncated."""
    if isinstance(o, dict):
        return {str(k)[:MAX_STR]: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        return None if np.isnan(o) or np.isinf(o) else round(float(o), 4)
    if isinstance(o, (pd.Timestamp, np.datetime64)):
        return str(pd.Timestamp(o))
    if o is pd.NaT or o is pd.NA:
        return None
    if isinstance(o, str):
        return o if len(o) <= MAX_STR else o[:MAX_STR] + "..."
    return o


def num(s):
    return pd.to_numeric(s, errors="coerce")


def dist(s):
    s = s.dropna()
    if s.empty:
        return {}
    return {"min": s.min(), "median": s.median(), "mean": s.mean(),
            "p95": s.quantile(.95), "max": s.max()}


def rows(df, idx, cols, k, samples):
    if not samples or len(idx) == 0:
        return []
    return df.loc[list(idx)[:k], cols].to_dict("records")


def multi_map(df, a, b, samples):
    """How many values of `a` map to more than one distinct `b`?"""
    pair = df[[a, b]].dropna().drop_duplicates()
    g = pair.groupby(a)[b].nunique()
    bad = g[g > 1].sort_values(ascending=False)
    res = {"keys": int(len(g)), "keys_with_multiple": int(len(bad)),
           "max_distinct": int(bad.iloc[0]) if len(bad) else 1}
    if samples and len(bad):
        res["examples"] = {str(k): [str(v) for v in pair.loc[pair[a] == k, b].head(4)]
                           for k in bad.index[:3]}
    return res


# ------------------------------------------------------- generic profiling
def numeric_profile(s):
    x = s.dropna()
    if x.empty:
        return {}
    q = x.quantile([.01, .25, .5, .75, .99])
    iqr = q[.75] - q[.25]
    lo, hi = q[.25] - 1.5 * iqr, q[.75] + 1.5 * iqr
    return {"min": x.min(), "p01": q[.01], "p25": q[.25], "median": q[.5],
            "p75": q[.75], "p99": q[.99], "max": x.max(), "mean": x.mean(),
            "std": x.std(), "zeros": int((x == 0).sum()),
            "negatives": int((x < 0).sum()),
            "iqr_outliers": int(((x < lo) | (x > hi)).sum()),
            "non_integer": int((x % 1 != 0).sum())}


def profile_columns(df, top_k):
    n, out = len(df), {}
    for c in df.columns:
        s = df[c]
        miss = int(s.isna().sum())
        info = {"dtype": str(s.dtype), "missing": miss,
                "missing_pct": round(100 * miss / n, 3) if n else 0,
                "nunique": int(s.nunique(dropna=True))}
        if pd.api.types.is_bool_dtype(s):
            info["top"] = s.value_counts().head(top_k).to_dict()
        elif pd.api.types.is_numeric_dtype(s):
            info["numeric"] = numeric_profile(s)
        elif pd.api.types.is_datetime64_any_dtype(s):
            info["min"], info["max"] = s.min(), s.max()
        else:
            x = s.dropna()
            types = x.map(lambda v: type(v).__name__).value_counts()
            if len(types) > 1:
                info["mixed_types"] = types.to_dict()
            st = x.astype(str)
            info["empty_or_whitespace"] = int((st.str.strip() == "").sum())
            info["leading_trailing_ws"] = int((st != st.str.strip()).sum())
            info["case_space_variants"] = int(
                st.nunique() - st.str.strip().str.lower().nunique())
            info["str_len"] = {"min": int(st.str.len().min()) if len(st) else None,
                               "max": int(st.str.len().max()) if len(st) else None}
            info["top"] = st.value_counts().head(top_k).to_dict()
        info["constant"] = info["nunique"] <= 1
        out[c] = info
    return out


# --------------------------------------------------- retail-specific checks
def retail_checks(df, R, top_k, samples):
    out, n = {}, len(df)
    g = lambda r: R.get(r)
    inv, stk, desc, qty, prc, cus, cty, dte = (
        g("invoice"), g("stock"), g("description"), g("quantity"),
        g("price"), g("customer"), g("country"), g("date"))
    q = num(df[qty]) if qty else None
    p = num(df[prc]) if prc else None
    invs = df[inv].astype("string").str.strip() if inv else None
    is_c = (invs.str.upper().str.startswith("C").fillna(False).astype(bool)
            if inv else None)
    base_cols = [c for c in (inv, stk, desc, qty, prc, cus, cty, dte) if c]

    # ---- invoices / cancellations
    if inv:
        prefix = invs.str.extract(r"^([A-Za-z]+)")[0]
        sec = {"n_invoices": int(invs.nunique()),
               "rows_with_letter_prefix": int(prefix.notna().sum()),
               "letter_prefix_counts": prefix.value_counts().head(top_k).to_dict(),
               "length_counts": invs.str.len().value_counts().head(10).to_dict(),
               "lines_per_invoice": dist(invs.value_counts()),
               "NOTE": "'C' prefix = cancellation HYPOTHESIS; verify vs prefix counts"}
        sec["rows_with_C_prefix"] = int(is_c.sum())
        sec["invoices_with_C_prefix"] = int(invs[is_c].nunique())
        if qty:
            sign = np.sign(q).map({-1.0: "neg", 0.0: "zero", 1.0: "pos"})
            lab = is_c.map({True: "C_prefix", False: "no_C_prefix"})
            sec["prefix_x_qty_sign"] = pd.crosstab(lab, sign).to_dict("index")
            t = pd.DataFrame({"i": invs, "neg": q < 0, "pos": q > 0})
            gg = t.groupby("i")[["neg", "pos"]].max()
            sec["invoices_with_mixed_qty_signs"] = int((gg.neg & gg.pos).sum())
            sec["samples_C_prefix_positive_qty"] = rows(
                df, df.index[is_c & (q > 0)], base_cols, 5, samples)
            sec["samples_noC_negative_qty"] = rows(
                df, df.index[~is_c & (q < 0)], base_cols, 5, samples)
        out["invoices"] = sec

    # ---- quantity
    if qty:
        out["quantity"] = {
            "non_numeric": int(q.isna().sum() - df[qty].isna().sum()),
            "negatives": int((q < 0).sum()), "zeros": int((q == 0).sum()),
            "largest_rows": rows(df, q.nlargest(5).index, base_cols, 5, samples),
            "smallest_rows": rows(df, q.nsmallest(5).index, base_cols, 5, samples)}

    # ---- price
    if prc:
        zero = df.index[p == 0]
        sec = {"non_numeric": int(p.isna().sum() - df[prc].isna().sum()),
               "negatives": int((p < 0).sum()), "zeros": int((p == 0).sum()),
               "largest_rows": rows(df, p.nlargest(5).index, base_cols, 5, samples),
               "zero_price_samples": rows(df, zero, base_cols, 5, samples)}
        if cus:
            sec["zero_price_rows_missing_customer"] = int(
                (df.loc[zero, cus].isna()).sum())
        if desc:
            sec["zero_price_top_descriptions"] = (
                df.loc[zero, desc].astype(str).value_counts().head(top_k).to_dict())
        if qty:
            sec["zero_price_qty_sign"] = (
                np.sign(q[p == 0]).value_counts().to_dict())
        out["price"] = sec

    # ---- customers
    if cus:
        c = df[cus]
        sec = {"missing_rows": int(c.isna().sum()),
               "missing_row_pct": round(100 * c.isna().mean(), 3),
               "n_customers": int(c.nunique())}
        cn = num(c)
        if c.notna().any() and cn.notna().any():
            sec["non_integer_ids"] = int((cn.dropna() % 1 != 0).sum())
        if inv:
            t = pd.DataFrame({"i": invs, "has": c.notna()})
            has = t.groupby("i")["has"].max()
            sec["invoices_without_any_customer"] = int((~has).sum())
            sec["invoices_total"] = int(len(has))
        if is_c is not None:
            sec["missing_customer_by_C_prefix"] = (
                c.isna().groupby(is_c).sum().rename(
                    {True: "C_prefix", False: "no_C_prefix"}).to_dict())
        if cty:
            sec["customers_with_multiple_countries"] = multi_map(
                df, cus, cty, samples)
        out["customers"] = sec

    # ---- products
    if stk or desc:
        sec = {}
        if stk:
            st = df[stk].dropna().astype(str).str.strip()
            shape = (st.str.replace(r"[A-Za-z]", "A", regex=True)
                       .str.replace(r"\d", "9", regex=True))
            sc = shape.value_counts()
            sec["n_stock_codes"] = int(st.nunique())
            sec["code_shape_counts"] = sc.head(top_k).to_dict()
            rare = st[shape.map(sc) / len(st) < 0.01]
            if len(rare):
                top = rare.value_counts().head(20)
                info = []
                for code, cnt in top.items():
                    row = {"code": code, "rows": int(cnt)}
                    if desc:
                        d = df.loc[df[stk].astype(str).str.strip() == code, desc]
                        d = d.dropna().astype(str)
                        row["top_description"] = d.mode().iloc[0] if len(d) else None
                    info.append(row)
                sec["rare_shape_codes_rows"] = int(len(rare))
                sec["rare_shape_codes_unique"] = int(rare.nunique())
                sec["rare_shape_codes_top20"] = info
        if desc:
            d = df[desc].dropna().astype(str)
            sec["description_missing"] = int(df[desc].isna().sum())
            sec["description_not_uppercase_rows"] = int((d != d.str.upper()).sum())
            sec["description_not_uppercase_examples"] = (
                d[d != d.str.upper()].value_counts().head(8).to_dict())
        if stk and desc:
            sec["stock_to_description"] = multi_map(df, stk, desc, samples)
            sec["description_to_stock"] = multi_map(df, desc, stk, samples)
        if stk and prc:
            sec["stock_to_price"] = multi_map(df, stk, prc, samples)
        out["products"] = sec

    # ---- countries
    if cty:
        vc = df[cty].astype(str).value_counts()
        out["countries"] = {"n": int(df[cty].nunique()),
                            "missing": int(df[cty].isna().sum()),
                            "rows_by_country": vc.head(60).to_dict()}

    # ---- dates
    if dte:
        d = df[dte] if pd.api.types.is_datetime64_any_dtype(df[dte]) \
            else pd.to_datetime(df[dte], errors="coerce")
        sec = {"unparseable": int(d.isna().sum() - df[dte].isna().sum()),
               "min": d.min(), "max": d.max(),
               "rows_by_month": d.dt.to_period("M").astype(str).value_counts()
                                 .sort_index().to_dict(),
               "rows_by_weekday": d.dt.day_name().value_counts().to_dict(),
               "hour_min": d.dt.hour.min(), "hour_max": d.dt.hour.max(),
               "distinct_days": int(d.dt.normalize().nunique())}
        if inv:
            tmp = df[[inv]].assign(_d=d)
            sec["invoice_to_timestamp"] = multi_map(tmp, inv, "_d", samples)
        out["dates"] = sec

    # ---- line totals (descriptive only)
    if qty and prc:
        lt = q * p
        sec = {"sum_positive": lt[lt > 0].sum(), "sum_negative": lt[lt < 0].sum(),
               "rows_total_zero": int((lt == 0).sum()), "dist": dist(lt)}
        if is_c is not None:
            sec["sum_by_C_prefix"] = lt.groupby(is_c).sum().rename(
                {True: "C_prefix", False: "no_C_prefix"}).to_dict()
        out["line_total_descriptive"] = sec

    # ---- grain / double counting
    grain = {"rows": n, "rows_per_invoice": dist(invs.value_counts()) if inv else None}
    combos = {
        "invoice+stock": [inv, stk],
        "invoice+stock+price": [inv, stk, prc],
        "invoice+stock+qty+price": [inv, stk, qty, prc],
        "invoice+stock+qty+price+date+customer": [inv, stk, qty, prc, dte, cus]}
    for name, cols in combos.items():
        if all(cols):
            dup = df.duplicated(subset=cols, keep=False)
            grain[f"rows_in_repeated_{name}"] = int(dup.sum())
            grain[f"extra_rows_{name}"] = int(df.duplicated(subset=cols).sum())
    out["grain"] = grain

    # ---- relationships
    rel = {}
    pairs = [(inv, cus), (inv, cty), (cus, cty)]
    for a, b in pairs:
        if a and b:
            rel[f"{a} -> {b}"] = multi_map(df, a, b, samples)
    num_cols = [c for c in df.select_dtypes("number").columns if c != cus]
    if len(num_cols) >= 2:
        sub = df[num_cols]
        if len(sub) > 200_000:
            sub = sub.sample(200_000, random_state=0)
        rel["spearman_numeric"] = sub.corr(method="spearman").round(3).to_dict()
    out["relationships"] = rel
    return out


# ------------------------------------------------------------ sheet audit
def audit_frame(df, overrides, top_k, samples):
    roles = detect_roles(list(df.columns), overrides)
    dup = df.duplicated()
    res = {
        "structure": {"rows": len(df), "columns": len(df.columns),
                      "column_names": list(df.columns),
                      "memory_mb": round(df.memory_usage(deep=True).sum() / 1e6, 1)},
        "roles": roles,
        "columns": profile_columns(df, top_k),
        "duplicates": {"full_row_duplicates": int(dup.sum()),
                       "pct": round(100 * dup.mean(), 4) if len(df) else 0,
                       "samples": df[dup].head(5).to_dict("records") if samples else []},
        "retail": retail_checks(df, roles, top_k, samples)}
    # light artifacts for cross-sheet checks (no raw data retained)
    art = {"hashes": pd.util.hash_pandas_object(df, index=False).values}
    if roles.get("invoice"):
        art["invoices"] = set(df[roles["invoice"]].dropna().astype(str))
    if roles.get("customer"):
        art["customers"] = set(df[roles["customer"]].dropna().astype(str))
    if roles.get("date"):
        d = pd.to_datetime(df[roles["date"]], errors="coerce")
        art["date_range"] = (d.min(), d.max())
    return res, art


def cross_sheet(arts):
    names = list(arts)
    out = {"sheets": names}
    allh = np.concatenate([arts[k]["hashes"] for k in names])
    out["total_rows"] = int(len(allh))
    out["duplicate_rows_across_all_sheets"] = int(len(allh) - len(np.unique(allh)))
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            key = f"{a} vs {b}"
            ov = {"identical_rows_in_both": int(len(
                np.intersect1d(arts[a]["hashes"], arts[b]["hashes"])))}
            for k in ("invoices", "customers"):
                if k in arts[a] and k in arts[b]:
                    ov[f"shared_{k}"] = len(arts[a][k] & arts[b][k])
            if "date_range" in arts[a] and "date_range" in arts[b]:
                (a0, a1), (b0, b1) = arts[a]["date_range"], arts[b]["date_range"]
                ov["date_ranges_overlap"] = bool(a0 <= b1 and b0 <= a1)
                ov["ranges"] = {a: [a0, a1], b: [b0, b1]}
            out[key] = ov
    return out


# --------------------------------------------------------------- reporting
def render_md(rep):
    L = ["# Data Audit Report", ""]
    f = rep["file"]
    L += [f"- file: `{f['name']}` | size: {f['size_mb']} MB | sha256: `{f['sha256']}`",
          f"- source unchanged after run: **{f['unchanged']}**",
          f"- generated: {rep['generated']} | runtime: {rep['runtime_s']}s", ""]
    for sheet, r in rep["sheets"].items():
        s = r["structure"]
        L += [f"## Sheet: {sheet}",
              f"rows={s['rows']:,} cols={s['columns']} mem={s['memory_mb']}MB",
              "", "### Detected roles (inferred from names - verify)",
              f"`{json.dumps(r['roles'])}`", "",
              "### Columns", "| column | dtype | missing | miss% | unique |",
              "|---|---|---|---|---|"]
        for c, i in r["columns"].items():
            L.append(f"| {c} | {i['dtype']} | {i['missing']} | "
                     f"{i['missing_pct']} | {i['nunique']} |")
        L += ["", "### Column detail (numeric stats / text hygiene / top values)"]
        for c, i in r["columns"].items():
            d = {k: v for k, v in i.items()
                 if k not in ("dtype", "missing", "missing_pct", "nunique")}
            L.append(f"- **{c}**: `{json.dumps(d, default=str, separators=(',', ':'))}`")
        L += ["", "### Duplicates",
              f"`{json.dumps(r['duplicates'], default=str, separators=(',', ':'))}`", ""]
        for name, sec in r["retail"].items():
            L += [f"### {name}",
                  f"`{json.dumps(sec, default=str, separators=(',', ':'))}`", ""]
    if "cross_sheet" in rep:
        L += ["## Cross-sheet checks",
              f"`{json.dumps(rep['cross_sheet'], default=str, separators=(',', ':'))}`"]
    return "\n".join(L)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--out", default="audit_output")
    ap.add_argument("--top-k", type=int, default=15)
    ap.add_argument("--sheets", nargs="*", help="subset of sheet names")
    ap.add_argument("--map", nargs="*", default=[], help='role="Column Name"')
    ap.add_argument("--no-samples", action="store_true", help="omit raw example rows")
    ap.add_argument("--max-chars", type=int, default=80_000)
    a = ap.parse_args()

    src = Path(a.path).resolve()
    out_dir = Path(a.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    overrides = dict(m.split("=", 1) for m in a.map)
    overrides = {k: v.strip('"') for k, v in overrides.items()}
    samples = not a.no_samples

    t0 = time.time()
    st0 = src.stat()
    print(f"Hashing source file ({st0.st_size/1e6:.1f} MB) ...")
    digest = sha256(src)

    report = {"file": {"name": src.name, "size_mb": round(st0.st_size / 1e6, 2),
                       "sha256": digest},
              "generated": time.strftime("%Y-%m-%d %H:%M:%S"), "sheets": {}}
    arts = {}

    if src.suffix.lower() in (".xlsx", ".xlsm", ".xls"):
        xl = pd.ExcelFile(src)
        names = [s for s in xl.sheet_names if not a.sheets or s in a.sheets]
        print(f"Sheets found: {xl.sheet_names}")
        load = lambda n: pd.read_excel(xl, sheet_name=n)
    else:
        names = ["csv"]
        def load(_):
            try:
                return pd.read_csv(src, low_memory=False)
            except UnicodeDecodeError:
                return pd.read_csv(src, low_memory=False, encoding="latin-1")

    for n in names:  # one sheet in memory at a time
        print(f"Reading + auditing sheet: {n} ...")
        df = load(n)
        res, art = audit_frame(df, overrides, a.top_k, samples)
        report["sheets"][n] = clean(res)
        arts[n] = art
        del df
        gc.collect()
        print(f"  done: {report['sheets'][n]['structure']['rows']:,} rows")

    if len(arts) > 1:
        report["cross_sheet"] = clean(cross_sheet(arts))

    st1 = src.stat()
    report["file"]["unchanged"] = (st0.st_size == st1.st_size
                                   and st0.st_mtime == st1.st_mtime)
    report["runtime_s"] = round(time.time() - t0, 1)

    md = render_md(report)
    (out_dir / "audit_report.md").write_text(md, encoding="utf-8")
    (out_dir / "audit_report.json").write_text(
        json.dumps(report, default=str, indent=1), encoding="utf-8")
    print(f"\nWrote {out_dir/'audit_report.md'}  ({len(md):,} chars, "
          f"~{len(md)//4:,} tokens)")
    if len(md) > a.max_chars:
        print("WARNING: report is large. Re-run with --top-k 8 or --no-samples.")
    print(f"Source file unchanged: {report['file']['unchanged']}")


if __name__ == "__main__":
    sys.exit(main())
