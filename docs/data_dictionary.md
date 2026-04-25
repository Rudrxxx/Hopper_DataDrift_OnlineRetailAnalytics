# Data Dictionary — Online Retail II

## Dataset Summary

| Item | Details |
|---|---|
| Dataset name | Online Retail II |
| Source | UCI Machine Learning Repository |
| Kaggle mirror | https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci |
| Raw file name | online_retail_II_raw.csv |
| Time period | December 2009 – December 2011 |
| Granularity | One row per product line per invoice (transaction line level) |
| Raw row count | ~1,067,371 |
| Cleaned row count | 1,027,017 |

## Original Column Definitions (Raw)

| Column Name | Data Type | Description | Example Value | Cleaning Notes |
|---|---|---|---|---|
| `Invoice` | string | Unique invoice number. Prefix 'C' indicates cancellation | `489434`, `C489449` | Kept as-is; used to flag cancellations |
| `StockCode` | string | Unique product code | `85123A` | Stripped whitespace |
| `Description` | string | Product description in free text | `WHITE HANGING HEART T-LIGHT HOLDER` | Title-cased, stripped; noise values removed |
| `Quantity` | integer | Units per line item | `6` | Rows with Quantity ≤ 0 removed (except cancellations) |
| `InvoiceDate` | datetime | Date and time of invoice | `12/1/2009 8:26` | Parsed to datetime; year/month/hour derived |
| `Price` | float | Unit price in GBP (£) | `2.55` | Rows with Price ≤ 0 removed (except cancellations) |
| `Customer ID` | float | Unique customer identifier (nullable) | `17850.0` | Nulls filled with 'GUEST'; trailing `.0` stripped |
| `Country` | string | Country of the customer | `United Kingdom` | Stripped and title-cased |

## Derived Columns (Added in ETL Pipeline)

| Derived Column | Logic | Business Meaning |
|---|---|---|
| `is_cancelled` | `Invoice.str.startswith('C')` | Boolean flag — True if the row belongs to a cancelled order |
| `year` | `InvoiceDate.dt.year` | Year of transaction — used for year-over-year analysis |
| `month` | `InvoiceDate.dt.month` | Month number — used for seasonality analysis |
| `month_name` | `InvoiceDate.dt.strftime('%B')` | Full month name — used as Tableau filter label |
| `quarter` | `InvoiceDate.dt.quarter` | Fiscal quarter (1–4) — Q4 shows consistent revenue spikes |
| `day_of_week` | `InvoiceDate.dt.day_name()` | Day name — reveals B2B purchasing patterns |
| `hour` | `InvoiceDate.dt.hour` | Hour of day — used for operational heatmap |
| `revenue` | `Quantity × Price` | Line-level revenue in GBP; negative for cancellations |
| `abs_revenue` | `abs(revenue)` | Absolute revenue — used to quantify cancellation value |
| `category` | `Description.split()[0]` | First keyword of description as proxy product category |

## KPI Definitions

| KPI | Formula | Business Meaning |
|---|---|---|
| Total Revenue | `sum(revenue)` where `is_cancelled = False` | Gross revenue from all completed sales |
| Average Order Value (AOV) | `Total Revenue / count(unique invoices, non-cancelled)` | Revenue generated per order — key profitability lever |
| Cancellation Rate | `count(cancelled invoices) / count(all invoices) × 100` | Percentage of orders that were cancelled — signals fulfilment or product issues |
| Revenue Lost to Cancellations | `sum(abs_revenue)` where `is_cancelled = True` | GBP value at risk from returns and cancellations |
| MoM Revenue Growth % | `(month_n - month_{n-1}) / month_{n-1} × 100` | Month-over-month growth rate — tracks business momentum |
| Customer Lifetime Value (proxy) | `sum(revenue) / count(unique customers)` per segment | Average total spend per customer — drives RFM targeting strategy |
| Pareto Threshold | % of SKUs generating 80% of revenue | Identifies strategic SKUs for inventory prioritization |

## Data Quality Notes

- **Missing Customer IDs (~25%):** Represent guest or anonymous checkouts. Retained with value `GUEST` to preserve revenue integrity; excluded from RFM segmentation.
- **Cancelled orders (~16%):** Invoices beginning with 'C' have negative quantities. Retained as a separate analytical dimension.
- **Noise descriptions:** Values like `?`, `POSTAGE`, `MANUAL`, `BANK CHARGES` removed — not product transactions.
- **Encoding:** Raw file uses ISO-8859-1 (Latin-1) due to special characters in product descriptions (e.g., accented letters).
- **Outliers:** Revenue values above the 99th percentile exist (bulk B2B orders). Not removed — legitimate transactions. Regression models cap at 99th percentile for stability.
- **Time gaps:** No transactions on weekends — dataset is B2B wholesale, not B2C retail.
