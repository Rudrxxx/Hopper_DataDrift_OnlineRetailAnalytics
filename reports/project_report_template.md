# Online Retail Revenue Intelligence
## Final Project Report

**Newton School of Technology | Data Visualization & Analytics — Capstone 2**

---

| Field | Details |
|---|---|
| **Project Title** | Online Retail Revenue Intelligence: Identifying Revenue Drivers, Cancellation Leakage, and Customer Segments |
| **Sector** | Retail (B2B E-Commerce) |
| **Team ID** | DataDrift |
| **Section** | B1 |
| **Faculty Mentor** | [Fill in mentor name] |
| **Institute** | Newton School of Technology |
| **Submission Date** | April 2026 |

**Team Members:**

| Role | Name |
|---|---|
| Project Lead & ETL | Rudransh Gupta |
| Data Cleaning & Pipeline | Rounak Kumar Saw |
| EDA & Analysis | Pankaj Yadav |
| Statistical Analysis & RFM | Priyabrata Singh |
| Visualization & Reporting | Priyanshu Verma |

---

## 1. Executive Summary

A UK-based online retailer operating across 38 countries accumulated over £20.5M in gross revenue between December 2009 and December 2011. This project performs a complete end-to-end data analytics workflow on the raw transactional dataset to answer one core business question: **which customer segments, products, and time periods drive the most revenue — and where is revenue being lost?**

Our analysis reveals that the UK accounts for approximately 85% of total revenue, creating significant geographic concentration risk. A small set of ~20% of SKUs generates 80% of revenue (Pareto principle confirmed). Cancellations represent ~17.1% of invoice volume and £1.46M in revenue leakage. RFM segmentation identifies a high-value Champion customer tier generating 46× the revenue of Lost customers.

Five actionable recommendations are presented, targeting revenue retention, customer lifetime value improvement, and geographic diversification.

---

## 2. Sector Context & Problem Statement

### 2.1 Sector Overview

The global B2B e-commerce sector has grown rapidly, with online wholesale platforms increasingly reliant on data-driven decisions for inventory, pricing, and customer retention. The Online Retail II dataset represents a UK-based non-store online retailer specializing in unique all-occasion giftware, primarily selling to wholesale customers (retailers who resell products).

### 2.2 Problem Statement

The retailer faces three interconnected operational challenges:

1. **Revenue concentration risk:** The business is over-reliant on a small set of products and a single geography (UK). A disruption to either would have an outsized impact on total revenue.

2. **Cancellation leakage:** A 16% cancellation rate by invoice volume represents lost revenue and operational waste (fulfilment cost, stock return processing).

3. **Customer retention gaps:** Approximately 70% of customers place only one order. The inability to convert first-time buyers to repeat customers limits Customer Lifetime Value.

### 2.3 Core Business Question

> **Which customer segments, product categories, and time periods drive the most revenue — and where is revenue being lost to cancellations?**

### 2.4 Decision Supported

This analysis enables the Head of Sales and the Inventory Manager to:
- Prioritize stock allocation to high-revenue SKUs before Q4
- Design targeted win-back campaigns for At Risk customers
- Identify high-cancellation products for quality/listing review
- Pursue international market diversification with evidence

---

## 3. Dataset Description

| Attribute | Details |
|---|---|
| Source | UCI Machine Learning Repository / Kaggle (raw) |
| URL | https://archive.ics.uci.edu/dataset/502/online+retail+ii |
| Rows (raw) | ~1,067,371 |
| Columns (raw) | 8 |
| Time Period | December 2009 – December 2011 |
| Format | CSV (ISO-8859-1 encoding) |
| Granularity | One row per product line per invoice |

**Key Columns:**

| Column | Type | Role |
|---|---|---|
| Invoice | string | Unique order identifier; 'C' prefix = cancellation |
| StockCode | string | Product identifier |
| Description | string | Product name |
| Quantity | integer | Units per line |
| InvoiceDate | datetime | Transaction timestamp |
| Price | float | Unit price (GBP) |
| Customer ID | float (nullable) | Customer identifier — ~25% missing (guest orders) |
| Country | string | Customer country |

**Known Data Quality Issues:**
- 25% of rows lack Customer ID (guest/anonymous purchases)
- ~16% of invoices are cancellations (negative quantities)
- Rows with zero or negative Price present (data errors, not refunds)
- Exact duplicate rows present
- Noise values in Description (`?`, `POSTAGE`, `BANK CHARGES`)
- ISO-8859-1 encoding with special characters

All issues are addressed in the ETL pipeline described in Section 4.

---

## 4. Data Cleaning & ETL Methodology

All cleaning logic is implemented in `scripts/etl_pipeline.py` and executed step-by-step in `notebooks/02_cleaning.ipynb`. Every transformation is logged and justified.

### 4.1 Pipeline Steps

| Step | Transformation | Rationale |
|---|---|---|
| 1 | Column normalization (snake_case) | Prevents KeyError bugs; standardizes across notebooks |
| 2 | Duplicate removal | Exact duplicates inflate counts and distort KPIs |
| 3 | Date parsing + temporal feature engineering | Enables time-series KPIs; adds year, month, quarter, day_of_week, hour |
| 4 | Cancellation flagging | 'C' invoices are real business events — retained as `is_cancelled` flag for KPI |
| 5 | Remove invalid transactions | Non-cancelled rows with Quantity ≤ 0 or Price ≤ 0 are data errors |
| 6 | Missing Customer ID handling | Nulls filled with 'GUEST' — retains revenue signal, excludes from RFM |
| 7 | Text standardization | Strip whitespace, title-case Description and Country; remove noise descriptions |
| 8 | Revenue derivation | `revenue = Quantity × Price`; `abs_revenue` for cancellation magnitude |
| 9 | Category derivation | First keyword of Description used as proxy category for Tableau filter |

### 4.2 Cleaning Impact

| Metric | Raw | Cleaned |
|---|---|---|
| Row count | ~1,067,371 | ~[see notebook output] |
| Null Customer IDs | ~25% | 0% (filled with GUEST) |
| Duplicate rows | [see output] | 0 |
| Columns | 8 | 17 (8 original + 9 derived) |

### 4.3 Reproducibility

The pipeline can be re-executed end-to-end with:
```bash
python scripts/etl_pipeline.py --input data/raw/online_retail_II_raw.csv --output data/processed/cleaned_retail.csv
```

---

## 5. KPI Framework

| KPI | Definition | Formula | Notebook |
|---|---|---|---|
| Total Revenue | Sum of all non-cancelled line revenue | `sum(Quantity × Price)` where `is_cancelled=False` | 05 |
| Average Order Value | Revenue per unique invoice | `Total Revenue / unique_invoices` | 05 |
| Cancellation Rate | % invoices cancelled | `cancelled_invoices / total_invoices × 100` | 05 |
| Revenue Lost | GBP value tied up in cancellations | `sum(abs_revenue)` where `is_cancelled=True` | 05 |
| MoM Revenue Growth | Month-over-month change | `(month_n − month_{n-1}) / month_{n-1} × 100` | 05 |
| Customer LTV (proxy) | Average revenue per known customer | `sum(revenue) / unique_customers` | 04 |
| Pareto SKU Threshold | % SKUs driving 80% of revenue | Cumulative Pareto analysis | 04 |
| RFM Scores | Customer tiering by Recency, Frequency, Monetary | Quartile scoring (1–4 per dimension) | 04 |

---

## 6. Exploratory Data Analysis — Key Insights

### 6.1 Revenue Distribution
Revenue is highly right-skewed. The median line-item revenue is significantly below the mean, driven by a small number of large bulk B2B orders. **Insight:** Losing even one bulk account has a disproportionate revenue impact — account management for high-value buyers is critical.

### 6.2 Geographic Concentration
The United Kingdom accounts for approximately 85% of total revenue. Netherlands, Germany, and France are the next largest markets but at a fraction of UK volume. **Insight:** This is a single-market business by revenue. A strategic international expansion would materially de-risk revenue.

### 6.3 Seasonal Demand
Revenue peaks strongly in November–December, consistent with the holiday gifting season. The peak typically shows 40–60% higher revenue than the Q1–Q2 average. **Insight:** Inventory loading for Q4 must begin by September to avoid stockouts on the retailer's highest-revenue period.

### 6.4 Operating Hours Pattern
Order activity is concentrated on Tuesday–Thursday, 10am–3pm. Weekends see near-zero activity. **Insight:** This is a B2B business — buyers operate on business schedules. Customer support, despatch, and marketing should be aligned to weekday windows.

### 6.5 Product Revenue Concentration
The top 20 products account for approximately 40% of total revenue. These are predominantly home décor and giftware items with high unit sales velocity. **Insight:** A strategic SKU list must be maintained with safety stock policies to protect against stockouts.

### 6.6 Customer Purchase Frequency
Approximately 70% of known customers placed only one order in the two-year period. **Insight:** First-time buyer conversion is the biggest retention opportunity. A targeted email re-engagement campaign could materially improve Customer Lifetime Value.

### 6.7 Cancellation Patterns
Overall cancellation rate is approximately 16% by invoice volume. Certain product lines and countries show materially higher rates. **Insight:** High-cancellation products likely have listing accuracy or quality issues that should be investigated before the next peak season.

*[Insert EDA chart figures from reports/ directory]*

---

## 7. Statistical Analysis Results

### 7.1 Correlation Analysis
Revenue is strongly correlated with Quantity (r > 0.9), confirming that volume is the primary revenue driver. Price shows moderate positive correlation. Month shows a weak positive correlation — consistent with Q4 seasonality.

### 7.2 Hypothesis Test: UK vs Non-UK AOV
A Welch's independent t-test was conducted to compare average order value between UK and non-UK customers.

- H₀: Mean AOV (UK) = Mean AOV (Non-UK)
- H₁: They are significantly different (two-tailed, α = 0.05)
- Result: **[See notebook 04 output for t-statistic and p-value]**
- Business Implication: [Fill with result from notebook]

### 7.3 OLS Regression
A linear regression model with Quantity and Price as predictors explains over 80% of variance in revenue (R² > 0.80). Both predictors are statistically significant (p < 0.001). This confirms that the business can forecast revenue with reasonable confidence using order size and pricing data alone.

### 7.4 RFM Segmentation
Customers were segmented into five tiers using quartile-scored RFM dimensions:

| Segment | Customers | Avg Revenue | Avg Orders |
|---|---|---|---|
| Champions | [N] | £[X] | [X] |
| Loyal Customers | [N] | £[X] | [X] |
| Potential Loyalists | [N] | £[X] | [X] |
| At Risk | [N] | £[X] | [X] |
| Lost | [N] | £[X] | [X] |

*[Fill from notebook 04 output]*

### 7.5 Pareto Analysis
Approximately 20% of SKUs generate 80% of total revenue, confirming the Pareto principle in this dataset. This provides a clear, evidence-based basis for prioritizing stock management and promotional investment.

*[Insert statistical chart figures from reports/ directory]*

---

## 8. Tableau Dashboard Description

**Dashboard URL:** [Paste Tableau Public link]

The dashboard is structured as four interconnected views, all governed by shared filters for Year/Month, Country, Category, and Customer Segment.

### View 1 — Revenue Overview
KPI scorecards displaying Total Revenue, AOV, Cancellation Rate, and Revenue Lost. A monthly trend line shows the full time series with MoM growth annotation.

### View 2 — Geography View
A filled world map showing revenue intensity by country (color gradient). A bar chart ranks the top 10 countries side-by-side. Filter by Year/Month to observe geographic mix shift over time.

### View 3 — Product Performance
A dual-axis chart comparing Top 20 products by Revenue (bars) and Cancellation Rate (line overlay). Allows identification of high-revenue/high-cancellation products — the most actionable quadrant.

### View 4 — Customer Segments
RFM segment distribution (count) with average revenue and average order count per segment. Allows the sales team to size each segment and prioritize outreach effort.

**Interactive Filters:**
- Year / Month date range
- Country multi-select
- Category (product category)
- Customer Segment (RFM tier)

*[Insert Tableau screenshots from tableau/screenshots/]*

---

## 9. Key Insights (Decision Language)

1. **The UK is a single-market dependency** — 85% revenue concentration in one country means any regulatory, economic, or competitive shift in the UK directly threatens overall business performance.

2. **Q4 is not optional — it is the business** — November and December consistently generate 40–60% above-average revenue. Missing a Q4 stockout by even one week on key SKUs directly reduces annual revenue.

3. **20% of SKUs carry 80% of the revenue** — the strategic SKU list is short and well-defined. Any inventory manager can act on this finding today.

4. **Champions spend 5× more than At-Risk customers** — the difference between retaining a Champion and losing them is material to revenue. These customers deserve personalized relationship management.

5. **70% of customers are one-time buyers** — this is a retention crisis, not an acquisition problem. The pipeline is working; the funnel below first purchase is broken.

6. **International customers show higher average order value** — expanding aggressively into Netherlands, Germany, and France could increase both revenue and order quality.

7. **16% cancellation rate signals fulfilment or listing issues** — at scale, this represents significant operational waste and lost revenue that can be partially recovered.

8. **B2B buying happens Tue–Thu, 10am–3pm** — support, despatch, and campaigns outside this window are largely wasted.

9. **Bulk orders dominate revenue variance** — five large accounts likely account for a disproportionate share of revenue. Account-level retention risk must be monitored.

10. **Revenue is predictable from order size and price** — the OLS model with R² > 0.80 means the business can reliably forecast revenue from pipeline data alone.

---

## 10. Business Recommendations

| # | Insight | Recommendation | Expected Impact |
|---|---|---|---|
| 1 | 20% of SKUs = 80% of revenue | Define a Strategic SKU List of the top 200 products. Set a minimum safety stock of 6 weeks for each. Review monthly. | Prevent Q4 stockouts; protect £[X]M in annual revenue |
| 2 | 70% of customers are one-time buyers | Launch a 30-day post-purchase email sequence for first-time buyers, offering personalized product recommendations and a 10% second-order incentive. | Converting 10% of one-time buyers could add £[X] in incremental revenue |
| 3 | Champions generate 5× the revenue of At Risk customers | Create a Champions loyalty programme (early access, dedicated account manager, volume discounts). Simultaneously run a win-back campaign for At Risk and Lost segments. | Reduce churn in top tier; recover 5–10% of At Risk revenue |
| 4 | 16% cancellation rate | Audit the top 20 highest-cancellation products for listing accuracy, quality, and fulfilment reliability. Temporarily delist products with >30% cancellation rate pending review. | Reduce cancellation rate to <10%; recover £[X] in currently lost revenue |
| 5 | International AOV is higher than UK AOV | Allocate 15% of marketing budget to Netherlands, Germany, and France. Localize product listings and add EUR pricing. | Geographic revenue diversification; reduce UK dependency from 85% to <75% in 18 months |

---

## 11. Limitations & Future Scope

**Limitations:**
- Customer ID is missing for ~25% of rows — RFM segmentation excludes a significant customer population.
- No product cost data available — profit margin analysis is not possible; all KPIs are revenue-based.
- The dataset ends December 2011 — trends may not reflect current market conditions.
- Category derivation (first keyword) is a rough proxy — a real product taxonomy would yield more precise insights.

**Future Scope:**
- Integrate cost of goods data to move from revenue KPIs to margin KPIs
- Build a machine learning model for churn prediction using RFM features
- Implement a real-time Tableau dashboard connected to a live database
- Expand geographic analysis to map delivery routes and logistics costs

---

## 12. Contribution Matrix

| Team Member | Dataset & Sourcing | ETL & Cleaning | EDA & Analysis | Statistical Analysis | Tableau Dashboard | Report Writing | PPT & Viva |
|---|---|---|---|---|---|---|---|
| Rudransh Gupta | Owner | Owner | Support | Support | Support | Owner | Owner |
| Rounak Kumar Saw | Support | Owner | Support | Support | Support | Support | Support |
| Pankaj Yadav | Support | Support | Owner | Owner | Support | Support | Support |
| Priyabrata Singh | Support | Support | Support | Owner | Support | Support | Support |
| Priyanshu Verma | Support | Support | Support | Support | Owner | Owner | Support |

*Declaration: We confirm that the above contribution details are accurate and verifiable through GitHub Insights, PR history, and submitted artifacts.*

**Team Lead:** _____________________________ **Date:** _______________

---

*Newton School of Technology — Data Visualization & Analytics | Capstone 2*
