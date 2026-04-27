# Online Retail Revenue Intelligence
### Team DataDrift | Newton School of Technology | Capstone 2 — Data Visualization & Analytics

---

## Team

| Role | Name |
|---|---|
| Project Lead & ETL | Rudransh Gupta |
| Data Cleaning & Pipeline | Rounak Kumar Saw |
| EDA & Analysis | Pankaj Yadav |
| Statistical Analysis & RFM | Priyabrata Singh |
| Visualization & Reporting | Priyanshu Verma |

---

## Problem Statement

A UK-based B2B online wholesale retailer sells giftware and home décor to buyers across 38 countries. This project performs a complete end-to-end data analytics workflow on two years of raw transactional data (December 2009 – December 2011) to answer one core business question:

> **Which customer segments, product categories, and time periods drive the most revenue — and where is revenue being lost to cancellations?**

**Sector:** Retail (B2B E-Commerce)

---

## Dataset

| Attribute | Value |
|---|---|
| Source | UCI Machine Learning Repository |
| Download | https://archive.ics.uci.edu/dataset/502/online+retail+ii |
| Kaggle mirror | https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci |
| Raw rows | 1,067,371 |
| Cleaned rows | 1,027,017 |
| Columns | 8 raw → 18 after feature engineering |
| Time period | December 2009 – December 2011 |
| Format | CSV, ISO-8859-1 encoded |

**Note:** The raw CSV file is committed to `data/raw/` and is never modified. All cleaning is performed in `notebooks/02_cleaning.ipynb` via `scripts/etl_pipeline.py`.

---

## ETL Pipeline Steps

All cleaning logic is modularized in `scripts/etl_pipeline.py` — 9 documented steps:

| Step | Transformation | Rationale |
|---|---|---|
| 1 | Column normalization (snake_case) | Prevents KeyError bugs across notebooks |
| 2 | Duplicate removal | 34,335 exact duplicates removed |
| 3 | Date parsing + temporal features | year, month, quarter, day_of_week, hour derived |
| 4 | Cancellation flagging | 19,104 cancelled rows flagged (not dropped) |
| 5 | Invalid transaction removal | 6,019 rows with qty≤0 or price≤0 removed |
| 6 | Missing Customer ID handling | 229,202 nulls filled with 'GUEST' |
| 7 | Text standardization | Description/Country cleaned; noise values removed |
| 8 | Revenue derivation | `revenue = Quantity × Price` |
| 9 | Category derivation | First keyword of Description as proxy category |

---

## KPI Dashboard

| KPI | Value |
|---|---|
| **Total Revenue** | £20,476,260.45 |
| **Average Order Value (AOV)** | £510.92 |
| **Cancellation Rate** | 17.1% |
| **Revenue Lost to Cancellations** | £1,462,797.75 |
| **Unique Customers** | 5,878 |
| **Unique Products** | 5,356 |
| **Total Orders** | 40,077 |
| **Average CLV** | £2,955.90 |
| **Repeat Rate** | 72.4% |

---

## Key Findings

1. **UK accounts for ~85% of total revenue** — significant geographic concentration risk
2. **Q4 (Nov–Dec) generates 40–60% above-average revenue** — inventory pre-loading is critical
3. **~20% of SKUs generate 80% of revenue** (Pareto confirmed)
4. **Champions segment generates 5× the revenue of At-Risk customers** (RFM segmentation)
5. **International customers show higher AOV** (£865.63 vs £476.53, p < 0.001)
6. **17.1% cancellation rate** — represents £1.46M in revenue leakage
7. **B2B buying patterns**: Tue–Thu, 10am–3pm — zero weekend activity

---

## Business Recommendations

| # | Recommendation | Expected Impact |
|---|---|---|
| 1 | Strategic SKU safety stock for top 200 products | Prevent Q4 stockouts |
| 2 | 30-day post-purchase email for first-time buyers | +10% repeat buyer conversion |
| 3 | Champions loyalty programme | Reduce top-tier churn |
| 4 | Audit high-cancellation products | Reduce cancel rate to <10% |
| 5 | International expansion: NL, DE, FR | Reduce UK dependency to <75% |

---

## Repository Structure

```
Hopper_DataDrift_OnlineRetailAnalytics/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/                        ← Original dataset (never edited)
│   │   └── online_retail_II_raw.csv
│   └── processed/                  ← Cleaned outputs from ETL pipeline
│       ├── cleaned_data.csv        ← Analysis-ready dataset
│       ├── kpi_summary.csv         ← Single-row KPI snapshot
│       ├── monthly_trends.csv      ← Monthly revenue aggregates
│       ├── country_kpis.csv        ← Country-level KPIs
│       ├── product_kpis.csv        ← Product-level KPIs
│       ├── rfm_segments.csv        ← Customer RFM segmentation
│       └── customer_summary.csv    ← Customer lifetime value data
├── notebooks/
│   ├── 01_extraction.ipynb         ← Data loading & quality audit
│   ├── 02_cleaning.ipynb           ← Full ETL pipeline (9 steps)
│   ├── 03_eda.ipynb                ← Exploratory data analysis
│   ├── 04_statistical_analysis.ipynb ← Correlation, t-test, regression, RFM, Pareto
│   └── 05_final_load_prep.ipynb    ← KPI computation & Tableau export
├── scripts/
│   ├── __init__.py
│   ├── etl_pipeline.py             ← Modular ETL functions (used by notebook 02)
│   └── run_all.py                  ← Master execution script
├── tableau/
│   ├── screenshots/                ← Dashboard screenshots
│   └── dashboard_links.md          ← Tableau Public URL
├── docs/
│   ├── data_dictionary.md          ← Full column & KPI definitions
│   └── github_contribution_guide.md
└── reports/
    ├── project_report_template.md
    ├── presentation_outline.md
    └── fig_*.png                   ← All EDA and statistical figures
```

---

## Tools Used

| Tool | Purpose |
|---|---|
| **Python 3.11+** | Core programming language |
| **Pandas** | Data manipulation and analysis |
| **NumPy** | Numerical computations |
| **Matplotlib** | Visualization and charting |
| **Seaborn** | Statistical visualizations |
| **SciPy** | Hypothesis testing (t-test) |
| **Statsmodels** | OLS regression analysis |
| **Jupyter Notebooks** | Interactive analysis workflow |
| **Tableau Public** | Interactive dashboards |

---

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/Rudrxxx/Hopper_DataDrift_OnlineRetailAnalytics.git
cd Hopper_DataDrift_OnlineRetailAnalytics
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the complete pipeline
```bash
python scripts/run_all.py
```
This generates all cleaned datasets, KPI files, and figures.

### 4. Or run notebooks individually (in order)
```
notebooks/01_extraction.ipynb
notebooks/02_cleaning.ipynb
notebooks/03_eda.ipynb
notebooks/04_statistical_analysis.ipynb
notebooks/05_final_load_prep.ipynb
```

### 5. Or run ETL standalone
```bash
python scripts/etl_pipeline.py \
  --input data/raw/online_retail_II_raw.csv \
  --output data/processed/cleaned_data.csv
```

---

## RFM Customer Segmentation

| Segment | Customers | Avg Revenue | Avg Orders | Avg Recency (days) |
|---|---|---|---|---|
| Champions | 1,740 | £8,056.42 | 15.22 | 37 |
| Loyal Customers | 1,186 | £1,585.78 | 4.41 | 117 |
| Potential Loyalists | 1,216 | £796.01 | 2.52 | 213 |
| At Risk | 1,165 | £350.47 | 1.39 | 351 |
| Lost | 571 | £174.53 | 1.00 | 547 |

---

## Statistical Analysis Summary

| Analysis | Method | Key Finding |
|---|---|---|
| Revenue drivers | Pearson correlation | Quantity is the primary revenue driver |
| UK vs Non-UK AOV | Welch's t-test | Non-UK AOV £865.63 vs UK £476.53 (p < 0.001) |
| Revenue prediction | OLS regression | Quantity + Price explain 55.6% of revenue variance |
| Customer segments | RFM scoring | Champions generate 46× more than Lost customers |
| Product concentration | Pareto analysis | ~20% of SKUs drive 80% of revenue |
| Seasonality | MoM growth rate | Q4 shows consistent positive growth spikes |

---

## Academic Integrity

All analysis, code, and recommendations are the original work of Hopper_DataDrift_OnlineRetailAnalytics. No pre-cleaned datasets were used.

---

*Newton School of Technology | Data Visualization & Analytics | Capstone 2*

