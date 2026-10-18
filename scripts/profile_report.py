#!/usr/bin/env python3
"""
profile_report.py
يقرأ جداول model/*.csv ويكتب تقريرًا واحدًا (Markdown) تُرسله لـ Claude.
قراءة فقط: لا يعدّل ولا يحذف أي ملف.

التشغيل:
    python profile_report.py --in clean_output/model --out analysis_report.md
"""
import argparse
import re
import traceback
from pathlib import Path

import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="indir", default="clean_output/model")
ap.add_argument("--out", default="analysis_report.md")
args = ap.parse_args()
IN = Path(args.indir)

L = []                                   # أسطر التقرير
w = lambda *x: L.extend(x)
f2 = lambda x: f"{x:,.2f}"


def md(df):
    """جدول Markdown بسيط (بدون الحاجة لمكتبة tabulate)."""
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in df.itertuples(index=False):
        out.append("| " + " | ".join(str(v).replace("|", "/") for v in r) + " |")
    return "\n".join(out)


def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def find(df, *cands):
    """يجد اسم العمود مهما اختلف الشكل (Customer ID / customer_id ...)."""
    m = {norm(c): c for c in df.columns}
    for c in cands:
        if norm(c) in m:
            return m[norm(c)]
    return None


def section(title):
    """ينفّذ القسم فورًا، وإذا فشل يسجّل الخطأ ويكمل بدل أن يتوقف التقرير."""
    def deco(fn):
        w("", f"## {title}")
        try:
            fn()
        except Exception as e:
            w(f"> فشل هذا القسم: `{type(e).__name__}: {e}`")
            traceback.print_exc()
        return fn
    return deco


# ---------------------------------------------------------------- القيم المرجعية من cleaning_log.md
EXP_ROWS = {"sales_lines": 1033062, "non_sales_lines": 11786, "invoices": 53628,
            "customers": 5875, "products": 4739, "calendar": 739}
EXP_TYPES = {"sale": 1015088, "cancellation": 17974, "stock_adjustment": 5913,
             "shipping": 3788, "fee_or_adjustment": 1906, "other_non_product": 118,
             "zero_price_item": 61, "unclassified": 0}
E_WITH = {"sale_lines": 1015088, "orders": 39516, "customers": 5852, "units": 11221957,
          "gross": 19700954.46, "returns": -719692.94, "net": 18981261.52, "aov": 498.56}
E_WITHOUT = {"sale_lines": 1003357, "orders": 39516, "customers": 5852, "units": 11188061,
             "gross": 19643861.64, "returns": -716462.57, "net": 18927399.07, "aov": 497.11}
LAB = {"sale_lines": "Sale lines", "orders": "Orders", "customers": "Customers",
       "units": "Units sold", "gross": "Gross product sales", "returns": "Returns",
       "net": "Net product revenue", "aov": "AOV (mean)", "aov_median": "AOV (median)"}
INTS = {"sale_lines", "orders", "customers", "units"}

# ---------------------------------------------------------------- تحميل الجداول
T = {}
w("# Analysis Profile Report", f"- المجلد: `{IN}`")
for n in EXP_ROWS:
    f = IN / f"{n}.csv"
    if f.exists():
        T[n] = pd.read_csv(f, low_memory=False)
    else:
        w(f"- **ملف غير موجود:** `{f}`")


@section("1. الجداول: الحجم والأعمدة وعيّنة")
def _():
    rows = [[n, f"{len(d):,}", f"{EXP_ROWS[n]:,}",
             "OK" if len(d) == EXP_ROWS[n] else "DIFF"] for n, d in T.items()]
    w(md(pd.DataFrame(rows, columns=["Table", "Rows", "Expected (log)", "Status"])))
    for n, d in T.items():
        info = pd.DataFrame({"column": d.columns, "dtype": d.dtypes.astype(str).values,
                             "nulls": d.isna().sum().values})
        w("", f"### {n}", md(info), "", "أول 3 صفوف:", md(d.head(3)))


if "sales_lines" not in T or "non_sales_lines" not in T:
    w("", "> لا يمكن إكمال بقية الأقسام دون `sales_lines` و`non_sales_lines`.")
else:
    S, N = T["sales_lines"], T["non_sales_lines"]

    def prep(df):
        g = lambda *c: find(df, *c)
        m = dict(_inv=g("Invoice", "InvoiceNo", "invoice_no"),
                 _qty=g("Quantity", "qty"),
                 _price=g("Price", "UnitPrice", "unit_price"),
                 _cust=g("Customer ID", "customer_id", "CustomerID"),
                 _type=g("row_type"),
                 _date=g("InvoiceDate", "invoice_date", "invoice_datetime", "date"),
                 _stock=g("StockCode", "stock_code"),
                 _country=g("Country"),
                 _dup=g("is_exact_duplicate"))
        for k, v in m.items():
            df[k] = df[v] if v is not None else None
        df["_inv"] = df["_inv"].astype(str).str.strip()
        df["_amt"] = df["_qty"] * df["_price"]
        df["_dup"] = (df["_dup"].astype(str).str.lower().isin(["true", "1", "1.0"])
                      if m["_dup"] else False)
        df["_date"] = pd.to_datetime(df["_date"], errors="coerce")
        return m

    mapping = prep(S)
    prep(N)
    s_all = S[S["_type"] == "sale"]
    c_all = S[S["_type"] == "cancellation"]

    @section("2. الأعمدة المكتشفة (تحقق أنها صحيحة)")
    def _():
        w(md(pd.DataFrame([[k.lstrip("_"), v] for k, v in mapping.items()],
                          columns=["role", "column in sales_lines"])))

    @section("3. توزيع row_type مقابل السجل")
    def _():
        cnt = pd.concat([S["_type"], N["_type"]]).value_counts()
        rows = [[t, f"{int(cnt.get(t, 0)):,}", f"{e:,}",
                 "OK" if int(cnt.get(t, 0)) == e else "DIFF"] for t, e in EXP_TYPES.items()]
        w(md(pd.DataFrame(rows, columns=["row_type", "Rows", "Expected (log)", "Status"])))

    def calc(drop):
        s, c = s_all, c_all
        if drop:
            s, c = s[~s["_dup"]], c[~c["_dup"]]
        g, r, o = s["_amt"].sum(), c["_amt"].sum(), s["_inv"].nunique()
        return {"sale_lines": len(s), "orders": o, "customers": s["_cust"].nunique(),
                "units": s["_qty"].sum(), "gross": g, "returns": r, "net": g + r,
                "aov": g / o, "aov_median": s.groupby("_inv")["_amt"].sum().median()}

    def cmp_table(res, exp):
        rows = []
        for k, lab in LAB.items():
            got, e = res[k], exp.get(k)
            fmt = (lambda x: f"{int(x):,}") if k in INTS else f2
            if e is None:
                rows.append([lab, fmt(got), "-", "-"])
                continue
            ok = got == e if k in INTS else abs(round(got, 2) - e) <= 0.011
            rows.append([lab, fmt(got), fmt(e), "OK" if ok else "DIFF"])
        return md(pd.DataFrame(rows, columns=["Metric", "Computed", "Expected (log D2)", "Status"]))

    @section("4. المقاييس الأساسية مقابل جدول D2")
    def _():
        w("### مع الصفوف المكررة (النسخة الأساسية)", cmp_table(calc(False), E_WITH))
        if S["_dup"].any():
            w("", "### بدون الصفوف المكررة (is_exact_duplicate)", cmp_table(calc(True), E_WITHOUT))
        else:
            w("", "> لا يوجد عمود is_exact_duplicate أو لا توجد قيم True فيه.")

    @section("5. Revenue Bridge")
    def _():
        r = calc(False)
        ship = N.loc[N["_type"] == "shipping", "_amt"].sum()
        fees = N.loc[N["_type"].isin(["fee_or_adjustment", "other_non_product"]), "_amt"].sum()
        b = [["Gross product sales", r["gross"]], ["Returns", r["returns"]],
             ["Net product revenue", r["net"]], ["Shipping", ship],
             ["Fees & adjustments (+ other_non_product)", fees],
             ["TOTAL", r["net"] + ship + fees]]
        w(md(pd.DataFrame([[k, f2(v)] for k, v in b], columns=["Item", "Amount"])))

    @section("6. التحقق من الطلبين الضخمين (D13)")
    def _():
        ids = ["581483", "C581484", "541431", "C541433"]
        d = S[S["_inv"].isin(ids)][["_inv", "_stock", "_qty", "_price", "_amt", "_type", "_cust", "_date"]]
        w(md(d.rename(columns=lambda c: c.lstrip("_"))))
        big_s = s_all.loc[s_all["_inv"].isin(ids[::2]), "_amt"].sum()
        big_c = c_all.loc[c_all["_inv"].isin(ids[1::2]), "_amt"].sum()
        r = calc(False)
        w("", md(pd.DataFrame([
            ["مبيعات الطلبين (sale)", f2(big_s)],
            ["إلغاء الطلبين (cancellation)", f2(big_c)],
            ["صافي الطلبين + إلغائهما", f2(big_s + big_c)],
            ["Gross بعد استبعاد الطلبين", f2(r["gross"] - big_s)],
            ["Returns بعد استبعاد الإلغاءين", f2(r["returns"] - big_c)],
        ], columns=["Item", "Value"])))

    @section("7. مطابقة جدول customers مع عملاء صفوف البيع")
    def _():
        Cu = T["customers"]
        cc = find(Cu, "Customer ID", "customer_id", "CustomerID")
        to_set = lambda x: set(pd.to_numeric(x, errors="coerce").dropna().astype("int64"))
        tab, sale_c, canc_c = to_set(Cu[cc]), to_set(s_all["_cust"]), to_set(c_all["_cust"])
        extra = tab - sale_c
        w(md(pd.DataFrame([
            ["عملاء جدول customers", f"{len(tab):,}"],
            ["عملاء لديهم صفوف sale", f"{len(sale_c):,}"],
            ["في الجدول وبلا أي sale", f"{len(extra):,}"],
            ["  منهم لديهم cancellation", f"{len(extra & canc_c):,}"],
            ["  منهم بلا sale ولا cancellation", f"{len(extra - canc_c):,}"],
        ], columns=["Item", "Count"])))

    @section("8. صفوف السعر الصفري مع Customer ID (ملاحظة D6)")
    def _():
        z = N[(N["_price"] == 0) & N["_cust"].notna()].groupby("_type").size()
        w(md(z.rename("rows").reset_index().rename(columns={"_type": "row_type"})))

    @section("9. المبيعات الشهرية (للتخطيط للمرحلة القادمة)")
    def _():
        m = s_all.groupby(s_all["_date"].dt.to_period("M")).agg(
            orders=("_inv", "nunique"), gross=("_amt", "sum")).reset_index()
        m["_date"] = m["_date"].astype(str)
        m["gross"] = m["gross"].map(f2)
        w(md(m.rename(columns={"_date": "month"})))

    @section("10. أعلى 10 دول حسب Gross")
    def _():
        g = s_all.groupby("_country")["_amt"].sum().sort_values(ascending=False)
        t = g.head(10).reset_index()
        t["share"] = (t["_amt"] / g.sum() * 100).round(2).astype(str) + "%"
        t["_amt"] = t["_amt"].map(f2)
        w(md(t.rename(columns={"_country": "country", "_amt": "gross"})))

out = Path(args.out)
out.write_text("\n".join(L), encoding="utf-8")
print(f"تم: {out.resolve()}")
