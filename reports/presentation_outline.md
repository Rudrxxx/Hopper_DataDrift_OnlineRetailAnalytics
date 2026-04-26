# Presentation Outline — Online Retail Revenue Intelligence

**Team DataDrift | Newton School of Technology | Capstone 2**
**Suggested deck length: 12–15 slides | Duration: 10 minutes + Q&A**

---

## Slide 1 — Title Slide
- Project title: **Online Retail Revenue Intelligence**
- Subtitle: *Identifying Revenue Drivers, Cancellation Leakage, and Customer Segments in B2B E-Commerce*
- Team: DataDrift | Newton School of Technology
- Date

---

## Slide 2 — The Business Problem
- **Who is the client?** A UK-based B2B online wholesale retailer, 38 countries, 2009–2011
- **What problem do they face?**
  - Revenue concentrated in UK (85%)
  - 17.1% cancellation rate → revenue leakage
  - 72.4% repeat rate, but CLV varies 46× across segments
- **Core question:** Which segments, products, and time periods drive revenue — and where is it lost?

---

## Slide 3 — Dataset & Methodology Overview
- Dataset: Online Retail II — UCI / Kaggle
- 1M+ rows | 8 columns | 2 years of transactions
- Pipeline: Python ETL → EDA → Statistical Analysis → Tableau
- Show GitHub repo structure diagram (screenshot)

---

## Slide 4 — Data Quality & ETL Pipeline
- Before/after table: raw vs cleaned row counts
- 9 cleaning steps (brief bullets)
- Highlight the hard problem: 25% missing Customer IDs → GUEST strategy
- "Every step logged and reproducible"

---

## Slide 5 — KPI Framework
Show the 7 KPIs as a clean scorecard:
- Total Revenue: £20.5M
- AOV: £510.92
- Cancellation Rate: 17.1%
- Revenue Lost: £1.46M
- Unique Customers: 5,878
- Champion CLV vs Lost CLV: £8,056 vs £175
- Pareto: ~20% SKUs = 80% revenue

---

## Slide 6 — Key Finding 1: Revenue Concentration (Geography)
- Bar chart: Top 10 countries by revenue
- UK = 85% → single-market risk
- "If UK demand drops 20%, total revenue drops 17%"

---

## Slide 7 — Key Finding 2: Seasonality
- Monthly revenue trend chart
- Q4 spike: Nov–Dec consistently 40–60% above average
- Heatmap: orders by day/hour → clear B2B pattern

---

## Slide 8 — Key Finding 3: Product Concentration (Pareto)
- Pareto curve chart
- ~20% of SKUs = 80% of revenue
- "Top 200 products need safety stock protection before October"

---

## Slide 9 — Key Finding 4: Customer Segmentation (RFM)
- RFM segment bar chart
- Champions vs Lost revenue comparison
- "Champions spend 5× more — they need a loyalty programme, not a newsletter"

---

## Slide 10 — Statistical Evidence
- Correlation matrix (revenue vs quantity/price)
- Hypothesis test result: UK vs Non-UK AOV (t-test, p < 0.001)
- Regression: R² = 0.56 — revenue is predictable from order size
- "We didn't just describe the data — we tested it"

---

## Slide 11 — Tableau Dashboard
- Full screenshot of dashboard
- Point out each view + filters
- Live demo if time allows (have URL ready)

---

## Slide 12 — 5 Business Recommendations
| # | Recommendation | Expected Impact |
|---|---|---|
| 1 | Strategic SKU safety stock policy | Prevent Q4 stockouts |
| 2 | First-buyer 30-day email sequence | +10% repeat buyer conversion |
| 3 | Champions loyalty programme | Reduce top-tier churn |
| 4 | Audit high-cancellation products | Reduce cancel rate to <10% |
| 5 | International expansion: NL, DE, FR | Reduce UK dependency to <75% |

---

## Slide 13 — Limitations & Next Steps
- Limitations: no cost data, missing CIDs, 2011 data
- Next steps: margin analysis, churn ML model, real-time dashboard

---

## Slide 14 — Team Contributions
- Contribution matrix (match GitHub)
- Each member's area of ownership

---

## Slide 15 — Thank You + Q&A
- GitHub repo link
- Tableau Public dashboard link
- "Questions?"

---

## Viva Preparation — Likely Questions

**Any team member may be asked:**
1. Why did you choose this dataset?
2. What does `is_cancelled` mean and how did you derive it?
3. What is AOV and how did you compute it?
4. Explain RFM segmentation in plain language.
5. What does the t-test result mean for the business?
6. What does R² = 0.56 mean in the regression?
7. What is the Pareto analysis showing?
8. Why did you keep GUEST customers instead of dropping them?
9. What are the limitations of using first keyword as a product category?
10. If you had 6 more months, what would you add?

