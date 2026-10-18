#!/usr/bin/env python3
"""
clean_phase_a.py  -  Phase A of the cleaning plan (steps 0-4).

    0. Load both sheets (read-only) + keep traceability columns
    1. Standardise types and text
    2. Resolve the cross-sheet overlap (the ONLY real deletion in the project)
    3. Flag exact duplicate rows (flag only, nothing deleted)
    4. Classify every row into exactly one row_type

Usage:
    python clean_phase_a.py online_retail_II.xlsx --out clean_output

Outputs (in --out, never over the source file):
    lines_all.parquet (or lines_all.csv.gz if pyarrow is missing)
    dropped_overlap_invoices.csv
    phase_a_report.md      <- share THIS file with the assistant

The original workbook is only READ. Size + mtime are verified at the end.
Console output is plain ASCII on purpose (Windows consoles + Arabic comments).
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------- settings
INV, STK, DESC, QTY, DATE, PRICE, CUST, CTRY = (
    "Invoice", "StockCode", "Description", "Quantity",
    "InvoiceDate", "Price", "Customer ID", "Country")
RAW_COLS = [INV, STK, DESC, QTY, DATE, PRICE, CUST, CTRY]

# قوائم الرموز اللي حددناها من الفحوص (بعد توحيد الحروف لـ UPPER)
SHIPPING = {"POST", "DOT", "C2"}
FEE_ADJ = {"B", "M", "D", "S", "BANK CHARGES", "ADJUST", "ADJUST2",
           "AMAZONFEE", "CRUK"}
TEST_OR_GIFT = {"TEST001", "TEST002", "GIFT"}      # + كل رمز يبدأ بـ GIFT_0001

# أرقام توقعناها من الفحوص السابقة (للمقارنة بس، مش شرط)
EXPECTED = {"shared_invoices": 1_088, "rows_after_overlap": 1_044_848,
            "exact_duplicates": 11_812}


# ------------------------------------------------------------------ step 0
def load(path):
    # الحركة 0: قرينا الورقتين من الإكسل (قراءة بس، ما لمسنا الملف الأصلي).
    # ضفنا عمودين: اسم الورقة ورقم السطر الأصلي بالإكسل، عشان نقدر نرجع
    # نتتبع أي صف لمكانه الأصلي.
    xl = pd.ExcelFile(path)
    sheets = xl.sheet_names
    if len(sheets) != 2:
        sys.exit(f"Expected 2 sheets, found {sheets}")
    frames = []
    for name in sheets:
        print(f"Reading sheet: {name} ...")
        df = pd.read_excel(xl, sheet_name=name)[RAW_COLS].copy()
        df["src_sheet"] = name
        df["src_row"] = np.arange(len(df)) + 2  # السطر 1 بالإكسل هو العناوين
        frames.append(df)
    d = pd.concat(frames, ignore_index=True)
    del frames

    # بصمة (hash) لكل صف بشكله الخام: نستعملها لاحقًا لمقارنة الورقتين
    # ولكشف المكرر، من غير ما نحتاج نقارن 8 أعمدة كل مرة.
    d["raw_hash"] = pd.util.hash_pandas_object(
        d[RAW_COLS].astype(str), index=False).values
    return sheets, d


# ------------------------------------------------------------------ step 1
def standardise(d):
    # الحركة 1: وحّدنا الأنواع والنصوص عشان نفس الشي يبان نفس الشي:
    # رقم الفاتورة نص بلا فراغات، ورمز المنتج نص بأحرف كبيرة (m = M)،
    # والوصف والدولة بلا فراغات زايدة، والعميل رقم صحيح بيقبل الفراغ.
    d["invoice"] = d[INV].astype(str).str.strip().fillna("")
    d["stock_code"] = d[STK].astype(str).str.strip().str.upper().fillna("")
    d["description"] = d[DESC].astype("string").str.strip()
    d["country"] = d[CTRY].astype("string").str.strip()
    d["quantity"] = pd.to_numeric(d[QTY], errors="coerce")
    d["price"] = pd.to_numeric(d[PRICE], errors="coerce")
    d["invoice_date"] = pd.to_datetime(d[DATE], errors="coerce")

    cust = pd.to_numeric(d[CUST], errors="coerce")
    if not (cust.dropna() % 1 == 0).all():
        sys.exit("Customer ID has non-integer values; stop and inspect.")
    d["customer_id"] = cust.astype("Int64")

    # شلنا الأعمدة الخام (الأصل محفوظ بالإكسل) عشان نوفر ذاكرة
    return d.drop(columns=RAW_COLS)


# ------------------------------------------------------------------ step 2
def resolve_overlap(d, sheets):
    # الحركة 2: الورقة الثانية أعادت تصدير أول 9 أيام من ديسمبر 2010.
    # قبل ما نحذف أي شي، تأكدنا برمجيًا إنو الفواتير المشتركة متطابقة تمامًا
    # (نفس الأسطر بالضبط) بالورقتين. إذا مش متطابقة البرنامج بيوقف.
    a = d[d.src_sheet == sheets[0]]
    b = d[d.src_sheet == sheets[1]]
    shared = sorted(set(a.invoice) & set(b.invoice))
    info = {"rows_loaded": len(d), "shared_invoices": len(shared)}

    if shared:
        ca = a[a.invoice.isin(shared)].groupby(["invoice", "raw_hash"]).size()
        cb = b[b.invoice.isin(shared)].groupby(["invoice", "raw_hash"]).size()
        if not ca.equals(cb):
            sys.exit("Shared invoices are NOT identical across sheets; "
                     "stop and inspect before dropping anything.")

    # وبعدين شلنا نسخة الورقة الثانية فقط (الأولى بتضل). هاد الحذف الحقيقي
    # الوحيد بالمشروع، وبنسجّل أرقام الفواتير المحذوفة بملف منفصل.
    drop = (d.src_sheet == sheets[1]) & d.invoice.isin(shared)
    info["overlap_rows_removed"] = int(drop.sum())
    return d[~drop].reset_index(drop=True), shared, info


# ------------------------------------------------------------------ step 3
def flag_duplicates(d):
    # الحركة 3: حطينا علامة is_exact_duplicate على النسخة التانية وما بعدها
    # من أي صف مكرر حرفيًا. ما حذفنا شي، لأنو قررنا نبقيهم ونعمل
    # sensitivity analysis (نقارن النتايج مع المكرر وبدونه).
    d["is_exact_duplicate"] = d.duplicated(subset=["raw_hash"], keep="first")
    return d


# ------------------------------------------------------------------ step 4
def classify(d):
    # الحركة 4: صنّفنا كل صف بنوع واحد بس (row_type). الترتيب مهم: أول شرط
    # بينطبق هو اللي بيحسم. وأي صف ما انطبق عليه شي بيروح "unclassified"،
    # ونتوقع يكون عددهم صفر.
    stk, inv = d.stock_code, d.invoice
    d["is_cancel_invoice"] = inv.str.upper().str.startswith("C")
    other_prefix = inv.str.match(r"^[A-Za-z]") & ~d.is_cancel_invoice  # فواتير A
    d["has_customer"] = d.customer_id.notna()

    def b(x):  # تحويل آمن لمصفوفة True/False
        return x.fillna(False).astype(bool).to_numpy()

    conditions = [
        b(stk.isin(SHIPPING)),                                  # شحن
        b(stk.isin(FEE_ADJ) | other_prefix),                    # رسوم/تعديلات
        b(stk.isin(TEST_OR_GIFT) | stk.str.startswith("GIFT_0001")),
        b((d.price == 0) & ~d.has_customer),                    # تسوية مخزون
        b((d.price == 0) & d.has_customer),                     # بند مجاني
        b(d.is_cancel_invoice),                                 # إلغاء
        b((d.quantity > 0) & (d.price > 0)),                    # بيع عادي
    ]
    names = ["shipping", "fee_or_adjustment", "other_non_product",
             "stock_adjustment", "zero_price_item", "cancellation", "sale"]
    d["row_type"] = np.select(conditions, names, default="unclassified")
    return d


# ---------------------------------------------------------------- reporting
def top(s, n=12):
    return (s.fillna("<missing>").value_counts().head(n)
             .rename_axis("value").reset_index(name="rows"))


def build_report(d, info, sheets, checks, unchanged, runtime, src):
    L = []
    w = L.append

    def T(df):
        w("```")
        w(df.to_string(index=False, max_colwidth=45) if len(df) else "(none)")
        w("```")

    w("# Phase A report (steps 0-4)")
    w(f"- source: `{src.name}` | unchanged after run: **{unchanged}** | "
      f"runtime {runtime:.0f}s")
    w(f"- sheets: {sheets}")
    w("")
    w("## Row-count waterfall")
    w(f"- rows loaded (both sheets): {info['rows_loaded']:,}")
    w(f"- shared invoices (identical in both sheets): {info['shared_invoices']:,}")
    w(f"- overlap rows removed (copy from sheet 2): {info['overlap_rows_removed']:,}")
    w(f"- rows after overlap resolution: {len(d):,}")
    w(f"- exact duplicate rows FLAGGED (kept): {int(d.is_exact_duplicate.sum()):,}")
    w("")
    w("## Rows by row_type")
    amt = d.quantity * d.price
    g = (d.assign(amount=amt).groupby("row_type")
          .agg(rows=("invoice", "size"), invoices=("invoice", "nunique"),
               units=("quantity", "sum"), amount=("amount", "sum"),
               pct_with_customer=("has_customer", "mean"),
               exact_dup_rows=("is_exact_duplicate", "sum")))
    g["share_pct"] = (100 * g.rows / len(d)).round(2)
    g["pct_with_customer"] = (100 * g.pct_with_customer).round(1)
    g["amount"] = g.amount.round(2)
    T(g.reset_index().sort_values("rows", ascending=False))
    w("(amount = Quantity x Price, descriptive only, NOT a result)")

    for t in ("shipping", "fee_or_adjustment", "other_non_product"):
        w("")
        w(f"### stock codes captured as `{t}`")
        T(top(d.loc[d.row_type == t, "stock_code"], 20))

    sa = d[d.row_type == "stock_adjustment"]
    w("")
    w("## stock_adjustment (zero price, no customer)")
    T(np.sign(sa.quantity).value_counts().rename_axis("qty_sign")
      .reset_index(name="rows"))
    w("top descriptions, quantity < 0:")
    T(top(sa.loc[sa.quantity < 0, "description"], 12))
    w("top descriptions, quantity > 0 (NOT inspected before):")
    T(top(sa.loc[sa.quantity > 0, "description"], 15))

    w("")
    w("## zero_price_item (zero price, WITH customer)")
    T(top(d.loc[d.row_type == "zero_price_item", "description"], 10))

    c = d[d.row_type == "cancellation"]
    w("")
    w("## cancellation")
    w(f"- rows: {len(c):,} | with quantity > 0: {int((c.quantity > 0).sum())} "
      f"| with customer: {c.has_customer.mean():.1%}")

    un = d[d.row_type == "unclassified"]
    w("")
    w(f"## unclassified rows: {len(un)}")
    T(un[["src_sheet", "src_row", "invoice", "stock_code", "description",
          "quantity", "price", "customer_id"]].head(20))

    w("")
    w("## Checks")
    for name, ok, detail in checks:
        w(f"- [{'PASS' if ok else 'CHECK'}] {name}: {detail}")
    return "\n".join(L)


def run_checks(d, info):
    cnt = d.row_type.value_counts()
    c = d[d.row_type == "cancellation"]
    ex = EXPECTED
    return [
        ("overlap verified identical before dropping", True,
         f"{info['shared_invoices']:,} shared invoices"),
        ("every row has exactly one type", int(cnt.sum()) == len(d),
         f"{int(cnt.sum()):,} typed vs {len(d):,} rows"),
        ("no unclassified rows", int(cnt.get("unclassified", 0)) == 0,
         f"{int(cnt.get('unclassified', 0))} found"),
        ("no cancellation with quantity > 0",
         int((c.quantity > 0).sum()) == 0, f"{int((c.quantity > 0).sum())} found"),
        ("shared invoices match diagnostics",
         info["shared_invoices"] == ex["shared_invoices"],
         f"{info['shared_invoices']:,} vs expected {ex['shared_invoices']:,}"),
        ("rows after overlap match diagnostics",
         len(d) == ex["rows_after_overlap"],
         f"{len(d):,} vs expected {ex['rows_after_overlap']:,}"),
        ("exact duplicates match diagnostics",
         int(d.is_exact_duplicate.sum()) == ex["exact_duplicates"],
         f"{int(d.is_exact_duplicate.sum()):,} vs expected ~{ex['exact_duplicates']:,}"),
    ]


# -------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--out", default="clean_output")
    a = ap.parse_args()

    src = Path(a.path).resolve()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    st0, t0 = src.stat(), time.time()

    sheets, d = load(src)
    d = standardise(d)
    d, shared, info = resolve_overlap(d, sheets)
    d = flag_duplicates(d)
    d = classify(d)
    checks = run_checks(d, info)

    # حفظنا النتايج بملفات جديدة (الأصل ما انلمس)
    pd.DataFrame({"invoice": shared}).to_csv(
        out / "dropped_overlap_invoices.csv", index=False)
    try:
        d.to_parquet(out / "lines_all.parquet", index=False)
        saved = "lines_all.parquet"
    except (ImportError, ValueError):
        d.to_csv(out / "lines_all.csv.gz", index=False)
        saved = "lines_all.csv.gz"

    st1 = src.stat()
    unchanged = st0.st_size == st1.st_size and st0.st_mtime == st1.st_mtime
    rep = build_report(d, info, sheets, checks, unchanged, time.time() - t0, src)
    (out / "phase_a_report.md").write_text(rep, encoding="utf-8")

    print("\nRow types:")
    print(d.row_type.value_counts().to_string())
    print("\nChecks:")
    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'CHECK'}] {name}: {detail}")
    print(f"\nSaved: {out / saved}")
    print(f"Report: {out / 'phase_a_report.md'}  (share this one)")
    print(f"Source file unchanged: {unchanged}")


if __name__ == "__main__":
    main()
