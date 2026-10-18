# Analysis notes and definitions

- **Orders:** The project defines an order as an invoice with at least one sale line; see `reports/phase_b_report.md`.
- **Gross product sales:** Product sales before returns.
- **Net product revenue:** Gross product sales plus negative return amounts under the project's classification rules.
- **D13 invoices:** Special invoice/cancellation pairs are flagged and excluded from selected gross/return views as documented in the reports.
- **Partial month:** December 2011 is marked as partial and should be excluded from full-month comparisons.
- **Outliers:** Large quantity/amount values are flagged for investigation; they are not automatically removed.
- **Duplicates:** Exact duplicate lines are flagged and a sensitivity comparison is reported; the default analysis keeps flagged duplicates.
