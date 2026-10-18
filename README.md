# Retail Intelligence & Customer Analytics — Online Retail II

A portfolio project analyzing retail transactions to understand sales performance, products, international markets, customer value, retention, and returns. The project combines Python-based data preparation and analysis with a multi-page Power BI dashboard.

## Project highlights

- Cleaned and classified transaction lines while preserving source traceability.
- Separated product sales from shipping, cancellations/returns, fees, and other non-product lines.
- Built analysis for monthly trends, product performance, country markets, customer RFM segmentation, cohort retention, and returns.
- Exported a Power BI-ready model with invoice facts and calendar, country, customer, and product dimensions.
- Added validation checks to compare key totals and model outputs.

## Selected findings

Based on the included analysis reports:

- **39,516 orders** were identified using the project's documented order definition.
- **£19.70M gross product sales** and **£18.98M net product revenue** were reported before the documented D13 exclusions/views.
- **£719.7K returns** were recorded as a negative amount in the model.
- **5,852 customers** had at least one order.
- The data covers **December 2009 through December 2011**, with December 2011 marked as a partial month.

These are project-defined metrics; consult the reports for the treatment of duplicate lines, cancellations, D13 invoice pairs, anonymous orders, and partial months.

## Dashboard

The Power BI report contains five pages:

1. **Overview** — headline sales and order KPIs.
2. **Markets** — country/market performance.
3. **Customers** — customer value and segmentation.
4. **Products** — product performance and concentration.
5. **Retention** — cohort-based repeat activity.

Dashboard screenshots are in [`screenshots/`](screenshots/). The Power BI file and PDF export are in [`powerbi/`](powerbi/).

## Tools

- Python
- Pandas, NumPy
- Matplotlib
- Power BI, Power Query, DAX
- CSV-based model exports

## Repository structure

```text
scripts/       Python cleaning, audit, analysis, and Power BI export scripts
reports/       Analysis reports, data-quality diagnostics, and validation results
powerbi/       Power BI report (.pbix), PDF export, and theme file
screenshots/   Dashboard page screenshots
```

## Reproducing the analysis

1. Download the **Online Retail II** dataset from the UCI Machine Learning Repository:
   https://archive.ics.uci.edu/dataset/502/online%2Bretail
2. Create a local working folder for the downloaded Excel workbook. Do not overwrite or modify the original file.
3. Install the packages listed in [`requirements.txt`](requirements.txt).
4. Run the cleaning scripts in order, then the analysis scripts. The scripts expect intermediate folders/files described in their docstrings; see each script's usage notes before running.
5. Open `powerbi/Online_Retail_Dashboard.pbix` in Power BI Desktop to explore the dashboard.

> The source workbook and intermediate CSV exports are intentionally not included in this repository. Download the dataset from UCI and generate the intermediate files locally. Some scripts rely on outputs from earlier steps, so they are not all standalone scripts.

## Data and limitations

The dataset is historical and covers 2009–2011. It contains invoice-level retail transactions, including cancellations and returns. Metrics depend on the project's documented business rules. Outliers are flagged for review rather than automatically removed, and the reports document key cleaning and validation decisions.

## Author

**Ali Yasser Dahi**  
LinkedIn: https://www.linkedin.com/in/ali-yasser-dahi-04277a401  
GitHub: https://github.com/aldahy334-ship-it

## Dataset citation

Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D
