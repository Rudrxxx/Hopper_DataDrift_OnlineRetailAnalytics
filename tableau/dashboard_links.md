# Tableau Dashboard Links

## Primary Dashboard

| Item | Details |
|---|---|
| **Dashboard Title** | Online Retail Revenue Intelligence Dashboard |
| **Tableau Public URL** | _[PASTE YOUR TABLEAU PUBLIC URL HERE AFTER PUBLISHING]_ |
| **Published By** | DVA_B1_T3 — Newton School of Technology |
| **Published Date** | _[Fill in date]_ |

## Dashboard Views

| View Name | Description | Sheet |
|---|---|---|
| Revenue Overview | KPI cards (Total Revenue, AOV, Cancellation Rate) + Monthly trend line | Sheet 1 |
| Geography View | Filled map of revenue by country + Top 10 countries bar chart | Sheet 2 |
| Product Performance | Top 20 products by revenue vs. cancellation rate (dual axis) | Sheet 3 |
| Customer Segments | RFM segment distribution + segment-level KPIs | Sheet 4 |

## Interactive Filters (Required)

- **Year / Month** — Date range filter applied to all views
- **Country** — Single or multi-select country filter
- **Category** — Product category filter (first keyword of description)
- **Customer Segment** — RFM segment filter (Champions, Loyal, At Risk, etc.)

## Data Sources Connected

| File | Used In |
|---|---|
| `data/processed/tableau_main.csv` | Primary source — all transaction-level views |
| `data/processed/monthly_kpis.csv` | Monthly trend chart |
| `data/processed/country_kpis.csv` | Geography map view |
| `data/processed/product_kpis.csv` | Product performance view |
| `data/processed/rfm_segments.csv` | Customer segment view |

## Screenshots

Dashboard screenshots are committed to `tableau/screenshots/`.

| File | Description |
|---|---|
| `screenshot_overview.png` | Revenue overview KPI page |
| `screenshot_geography.png` | Country map view |
| `screenshot_products.png` | Product performance view |
| `screenshot_segments.png` | RFM customer segment view |

