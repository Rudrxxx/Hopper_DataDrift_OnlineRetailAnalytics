"""
Master Execution Script — Online Retail Revenue Intelligence
=============================================================
This script runs the entire pipeline end-to-end and generates ALL outputs:
  1. Cleaned dataset (cleaned_retail.csv + cleaned_data.csv)
  2. KPI summary files (kpi_summary.csv, customer_summary.csv, monthly_trends.csv)
  3. Country/Product/RFM exports
  4. All EDA and statistical analysis figures
  5. Tableau-ready main export

Usage:
    python scripts/run_all.py

All outputs are saved to data/processed/ and reports/.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Ensure we can import from scripts/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
import warnings
warnings.filterwarnings("ignore")

from scripts.etl_pipeline import run_full_pipeline, save_processed

# ── Paths ──────────────────────────────────────────────────────────────────
RAW_PATH      = PROJECT_ROOT / "data" / "raw" / "online_retail_II_raw.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR   = PROJECT_ROOT / "reports"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Set up plot style
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor"  : "white",
    "axes.spines.top" : False,
    "axes.spines.right": False,
    "font.size"       : 11,
})


def main():
    print("=" * 70)
    print("  ONLINE RETAIL REVENUE INTELLIGENCE — FULL PIPELINE EXECUTION")
    print("=" * 70)

    # ================================================================
    # PHASE 1: ETL Pipeline
    # ================================================================
    print("\n" + "─" * 70)
    print("PHASE 1: ETL Pipeline — Load, Clean, Transform")
    print("─" * 70)

    df = run_full_pipeline(RAW_PATH)

    # Save as both cleaned_retail.csv (for notebooks) and cleaned_data.csv (user requirement)
    save_processed(df, PROCESSED_DIR / "cleaned_retail.csv")
    save_processed(df, PROCESSED_DIR / "cleaned_data.csv")
    print(f"  → Cleaned dataset saved: {df.shape}")

    df_sales = df[~df["is_cancelled"]].copy()
    print(f"  → Sales rows (non-cancelled): {len(df_sales):,}")

    # ================================================================
    # PHASE 2: KPI Computation
    # ================================================================
    print("\n" + "─" * 70)
    print("PHASE 2: KPI Computation")
    print("─" * 70)

    # ── Core KPIs ──
    total_revenue      = df_sales["revenue"].sum()
    unique_orders      = df_sales["invoice"].nunique()
    aov                = total_revenue / unique_orders
    total_invoices     = df["invoice"].nunique()
    cancelled_invoices = df[df["is_cancelled"]]["invoice"].nunique()
    cancellation_rate  = cancelled_invoices / total_invoices * 100
    revenue_lost       = df[df["is_cancelled"]]["abs_revenue"].sum()
    unique_customers   = df_sales[df_sales["customer_id"] != "GUEST"]["customer_id"].nunique()
    unique_products    = df_sales["description"].nunique()

    print(f"  Total Revenue         : £{total_revenue:>15,.2f}")
    print(f"  Average Order Value   : £{aov:>15,.2f}")
    print(f"  Cancellation Rate     :  {cancellation_rate:>14.1f}%")
    print(f"  Revenue Lost (cancels): £{revenue_lost:>15,.2f}")
    print(f"  Unique Customers      :  {unique_customers:>14,}")
    print(f"  Unique Products       :  {unique_products:>14,}")
    print(f"  Total Orders          :  {unique_orders:>14,}")

    # ── KPI Summary CSV ──
    kpi_summary = pd.DataFrame([{
        "total_revenue":       round(total_revenue, 2),
        "average_order_value": round(aov, 2),
        "cancellation_rate_pct": round(cancellation_rate, 2),
        "revenue_lost_to_cancellations": round(revenue_lost, 2),
        "unique_customers":    unique_customers,
        "unique_products":     unique_products,
        "total_orders":        unique_orders
    }])
    kpi_summary.to_csv(PROCESSED_DIR / "kpi_summary.csv", index=False)
    print("  → Saved: kpi_summary.csv")

    # ── Monthly Trends CSV ──
    monthly = (
        df_sales.groupby(["year", "month", "month_name"]).agg(
            revenue=("revenue", "sum"),
            orders=("invoice", "nunique"),
            items_sold=("quantity", "sum"),
            unique_customers=("customer_id", "nunique")
        ).reset_index().sort_values(["year", "month"])
    )
    monthly["aov"] = (monthly["revenue"] / monthly["orders"]).round(2)
    monthly["mom_growth"] = monthly["revenue"].pct_change().mul(100).round(2)
    monthly["period"] = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)
    monthly.to_csv(PROCESSED_DIR / "monthly_kpis.csv", index=False)
    monthly.to_csv(PROCESSED_DIR / "monthly_trends.csv", index=False)
    print("  → Saved: monthly_kpis.csv, monthly_trends.csv")

    # ── Country KPIs CSV ──
    country_kpis = (
        df_sales.groupby("country").agg(
            revenue=("revenue", "sum"),
            orders=("invoice", "nunique"),
            unique_customers=("customer_id", "nunique"),
            items_sold=("quantity", "sum")
        ).reset_index()
    )
    country_kpis["aov"] = (country_kpis["revenue"] / country_kpis["orders"]).round(2)
    country_kpis["revenue_share"] = (country_kpis["revenue"] / country_kpis["revenue"].sum() * 100).round(2)
    cancel_country = (
        df.groupby("country").agg(
            total_inv=("invoice", "nunique"),
            cancel_inv=("is_cancelled", "sum")
        ).reset_index()
    )
    cancel_country["cancellation_rate"] = (cancel_country["cancel_inv"] / cancel_country["total_inv"] * 100).round(2)
    country_kpis = country_kpis.merge(cancel_country[["country", "cancellation_rate"]], on="country", how="left")
    country_kpis.sort_values("revenue", ascending=False).to_csv(PROCESSED_DIR / "country_kpis.csv", index=False)
    print("  → Saved: country_kpis.csv")

    # ── Product KPIs CSV ──
    product_kpis = (
        df_sales.groupby(["stockcode", "description", "category"]).agg(
            revenue=("revenue", "sum"),
            qty_sold=("quantity", "sum"),
            orders=("invoice", "nunique"),
            avg_price=("price", "mean")
        ).reset_index()
    )
    cancel_prod = (
        df.groupby("stockcode").agg(
            total_lines=("invoice", "count"),
            cancel_lines=("is_cancelled", "sum")
        ).reset_index()
    )
    cancel_prod["cancel_rate"] = (cancel_prod["cancel_lines"] / cancel_prod["total_lines"] * 100).round(2)
    product_kpis = product_kpis.merge(cancel_prod[["stockcode", "cancel_rate"]], on="stockcode", how="left")
    product_kpis["revenue_share"] = (product_kpis["revenue"] / product_kpis["revenue"].sum() * 100).round(4)
    product_kpis["avg_price"] = product_kpis["avg_price"].round(2)
    product_kpis.sort_values("revenue", ascending=False).to_csv(PROCESSED_DIR / "product_kpis.csv", index=False)
    print("  → Saved: product_kpis.csv")

    # ── Customer Summary CSV ──
    known = df_sales[df_sales["customer_id"] != "GUEST"]
    customer_summary = known.groupby("customer_id").agg(
        total_revenue=("revenue", "sum"),
        total_orders=("invoice", "nunique"),
        total_items=("quantity", "sum"),
        first_purchase=("invoicedate", "min"),
        last_purchase=("invoicedate", "max"),
        avg_order_value=("revenue", "mean"),
    ).reset_index()
    customer_summary["total_revenue"] = customer_summary["total_revenue"].round(2)
    customer_summary["avg_order_value"] = customer_summary["avg_order_value"].round(2)

    # CLV = total_revenue per customer
    # Repeat Rate
    repeat_customers = (customer_summary["total_orders"] > 1).sum()
    total_cust = len(customer_summary)
    repeat_rate = repeat_customers / total_cust * 100 if total_cust > 0 else 0

    print(f"\n  Customer Lifetime Value (CLV) avg: £{customer_summary['total_revenue'].mean():,.2f}")
    print(f"  Repeat Rate: {repeat_rate:.1f}% ({repeat_customers:,} / {total_cust:,})")

    customer_summary.sort_values("total_revenue", ascending=False).to_csv(
        PROCESSED_DIR / "customer_summary.csv", index=False
    )
    print("  → Saved: customer_summary.csv")

    # ── RFM Segments CSV ──
    rfm_df = df_sales[df_sales["customer_id"] != "GUEST"].copy()
    snapshot_date = rfm_df["invoicedate"].max() + pd.Timedelta(days=1)
    rfm = rfm_df.groupby("customer_id").agg(
        recency=("invoicedate", lambda x: (snapshot_date - x.max()).days),
        frequency=("invoice", "nunique"),
        monetary=("revenue", "sum")
    ).reset_index()
    rfm["r_score"] = pd.qcut(rfm["recency"],   q=4, labels=[4, 3, 2, 1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"),  q=4, labels=[1, 2, 3, 4]).astype(int)
    rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]

    def rfm_segment(score):
        if score >= 10: return "Champions"
        elif score >= 8: return "Loyal Customers"
        elif score >= 6: return "Potential Loyalists"
        elif score >= 4: return "At Risk"
        else: return "Lost"

    rfm["segment"] = rfm["rfm_score"].apply(rfm_segment)
    rfm["monetary"] = rfm["monetary"].round(2)
    rfm.to_csv(PROCESSED_DIR / "rfm_segments.csv", index=False)
    print("  → Saved: rfm_segments.csv")

    segment_summary = rfm.groupby("segment").agg(
        customers=("customer_id", "count"),
        avg_revenue=("monetary", "mean"),
        avg_orders=("frequency", "mean"),
        avg_recency=("recency", "mean")
    ).round(2).sort_values("avg_revenue", ascending=False)
    print("\n  RFM Segment Summary:")
    print(segment_summary.to_string())

    # ── Tableau Main CSV ──
    tableau_cols = [
        "invoice", "stockcode", "description", "category",
        "quantity", "invoicedate", "price", "revenue", "abs_revenue",
        "customer_id", "country",
        "year", "month", "month_name", "quarter", "day_of_week", "hour",
        "is_cancelled"
    ]
    tableau_cols = [c for c in tableau_cols if c in df.columns]
    tableau_df = df[tableau_cols].copy()
    tableau_df.to_csv(PROCESSED_DIR / "tableau_main.csv", index=False)
    print(f"  → Saved: tableau_main.csv ({tableau_df.shape})")

    # ================================================================
    # PHASE 3: EDA Figures
    # ================================================================
    print("\n" + "─" * 70)
    print("PHASE 3: Exploratory Data Analysis — Generating Figures")
    print("─" * 70)

    # ── Fig 01: Missing Values ──
    raw_df = pd.read_csv(RAW_PATH, encoding="ISO-8859-1")
    missing = pd.DataFrame({
        "Missing Count": raw_df.isna().sum(),
        "Missing %":     (raw_df.isna().sum() / len(raw_df) * 100).round(2)
    }).sort_values("Missing %", ascending=False)
    cols_with_missing = missing[missing["Missing %"] > 0]
    if len(cols_with_missing) > 0:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.barh(cols_with_missing.index, cols_with_missing["Missing %"], color="#E24B4A")
        ax.set_xlabel("Missing %")
        ax.set_title("Missing Values by Column")
        ax.xaxis.set_major_formatter(mticker.PercentFormatter())
        plt.tight_layout()
        plt.savefig(REPORTS_DIR / "fig_01_missing_values.png", dpi=150)
        plt.close()
        print("  → Saved: fig_01_missing_values.png")

    # ── Fig 03a: Revenue Distribution ──
    rev_cap = df_sales["revenue"].quantile(0.99)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4))
    df_sales[df_sales["revenue"] <= rev_cap]["revenue"].hist(
        bins=60, ax=axes[0], color="#378ADD", edgecolor="white"
    )
    axes[0].set_title("Revenue Distribution (capped at 99th pct)", fontweight="bold")
    axes[0].set_xlabel("Revenue (£)")
    axes[0].set_ylabel("Frequency")
    axes[1].boxplot(df_sales["revenue"].clip(0, rev_cap), vert=False, patch_artist=True,
                    boxprops=dict(facecolor="#378ADD", alpha=0.6))
    axes[1].set_title("Revenue Boxplot (outlier detection)", fontweight="bold")
    axes[1].set_xlabel("Revenue (£)")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "fig_03a_revenue_distribution.png", dpi=150)
    plt.close()
    print("  → Saved: fig_03a_revenue_distribution.png")

    # ── Fig 03b: Revenue by Country ──
    country_rev = (
        df_sales.groupby("country")["revenue"]
        .sum().sort_values(ascending=False).head(12).reset_index()
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#185FA5" if c == "United Kingdom" else "#85B7EB" for c in country_rev["country"]]
    ax.barh(country_rev["country"][::-1], country_rev["revenue"][::-1], color=colors[::-1])
    ax.set_xlabel("Total Revenue (£)")
    ax.set_title("Top 12 Countries by Revenue", fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e6:.1f}M"))
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "fig_03b_revenue_by_country.png", dpi=150)
    plt.close()
    print("  → Saved: fig_03b_revenue_by_country.png")

    # ── Fig 03c: Monthly Revenue Trend ──
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(monthly["period"], monthly["revenue"], marker="o", linewidth=2,
            color="#185FA5", markersize=5)
    ax.fill_between(range(len(monthly)), monthly["revenue"], alpha=0.12, color="#185FA5")
    ax.set_xticks(range(len(monthly)))
    ax.set_xticklabels(monthly["period"], rotation=45, ha="right", fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e6:.1f}M"))
    ax.set_title("Monthly Revenue Trend (2009–2011)", fontweight="bold")
    ax.set_ylabel("Revenue (£)")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "fig_03c_monthly_trend.png", dpi=150)
    plt.close()
    print("  → Saved: fig_03c_monthly_trend.png")

    # ── Fig 03d: Orders Heatmap ──
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_data = (
        df_sales.groupby(["day_of_week", "hour"])["invoice"]
        .nunique().unstack(fill_value=0).reindex(day_order)
    )
    fig, ax = plt.subplots(figsize=(14, 4))
    sns.heatmap(heatmap_data, ax=ax, cmap="Blues", linewidths=0.3,
                cbar_kws={"label": "Unique Orders"})
    ax.set_title("Order Volume by Day of Week and Hour", fontweight="bold")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "fig_03d_heatmap_orders.png", dpi=150)
    plt.close()
    print("  → Saved: fig_03d_heatmap_orders.png")

    # ── Fig 03e: Top Products ──
    product_rev = (
        df_sales.groupby("description")["revenue"]
        .sum().sort_values(ascending=False).head(20).reset_index()
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(product_rev["description"][::-1], product_rev["revenue"][::-1], color="#1D9E75")
    ax.set_xlabel("Total Revenue (£)")
    ax.set_title("Top 20 Products by Revenue", fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}K"))
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "fig_03e_top_products.png", dpi=150)
    plt.close()
    print("  → Saved: fig_03e_top_products.png")

    # ── Fig 03f: Customer Frequency ──
    freq = known.groupby("customer_id")["invoice"].nunique()
    fig, ax = plt.subplots(figsize=(10, 4))
    freq.clip(upper=30).hist(bins=30, ax=ax, color="#D85A30", edgecolor="white")
    ax.set_title("Customer Purchase Frequency (capped at 30)", fontweight="bold")
    ax.set_xlabel("Number of Orders")
    ax.set_ylabel("Number of Customers")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "fig_03f_customer_frequency.png", dpi=150)
    plt.close()
    print("  → Saved: fig_03f_customer_frequency.png")

    # ================================================================
    # PHASE 4: Statistical Analysis Figures
    # ================================================================
    print("\n" + "─" * 70)
    print("PHASE 4: Statistical Analysis — Generating Figures")
    print("─" * 70)

    # ── Fig 04a: Correlation Matrix ──
    corr_cols = ["quantity", "price", "revenue", "month", "hour"]
    corr_matrix = df_sales[corr_cols].corr()
    fig, ax = plt.subplots(figsize=(7, 5))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                ax=ax, square=True, linewidths=0.5, mask=mask)
    ax.set_title("Correlation Matrix — Key Numerical Variables", fontweight="bold")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "fig_04a_correlation.png", dpi=150)
    plt.close()
    print("  → Saved: fig_04a_correlation.png")

    # ── Fig 04b: RFM Segments ──
    seg_counts = rfm["segment"].value_counts()
    colors_rfm = ["#185FA5", "#1D9E75", "#BA7517", "#E24B4A", "#888780"]
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(seg_counts.index, seg_counts.values, color=colors_rfm[:len(seg_counts)])
    ax.set_title("Customer Count by RFM Segment", fontweight="bold")
    ax.set_ylabel("Customers")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "fig_04b_rfm_segments.png", dpi=150)
    plt.close()
    print("  → Saved: fig_04b_rfm_segments.png")

    # ── Fig 04c: Pareto Analysis ──
    pareto_rev = (
        df_sales.groupby("description")["revenue"]
        .sum().sort_values(ascending=False).reset_index()
    )
    pareto_rev["cumulative_pct"] = pareto_rev["revenue"].cumsum() / pareto_rev["revenue"].sum() * 100
    pareto_rev["product_pct"] = np.arange(1, len(pareto_rev)+1) / len(pareto_rev) * 100
    threshold_80 = pareto_rev[pareto_rev["cumulative_pct"] <= 80]
    pct_products = len(threshold_80) / len(pareto_rev) * 100

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(pareto_rev["product_pct"], pareto_rev["cumulative_pct"],
            color="#185FA5", linewidth=2)
    ax.axhline(80, color="#E24B4A", linestyle="--", linewidth=1.5, label="80% revenue line")
    ax.axvline(pct_products, color="#BA7517", linestyle="--", linewidth=1.5,
               label=f"{pct_products:.1f}% of products")
    ax.set_xlabel("% of Products (ranked by revenue)")
    ax.set_ylabel("Cumulative Revenue %")
    ax.set_title("Pareto Analysis — Product Revenue Concentration", fontweight="bold")
    ax.legend()
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "fig_04c_pareto.png", dpi=150)
    plt.close()
    print("  → Saved: fig_04c_pareto.png")

    # ── Fig 04d: MoM Growth ──
    fig, ax = plt.subplots(figsize=(13, 4))
    colors_mom = ["#1D9E75" if x >= 0 else "#E24B4A" for x in monthly["mom_growth"].fillna(0)]
    ax.bar(monthly["period"], monthly["mom_growth"].fillna(0), color=colors_mom)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(range(len(monthly)))
    ax.set_xticklabels(monthly["period"], rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("MoM Growth %")
    ax.set_title("Month-over-Month Revenue Growth", fontweight="bold")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "fig_04d_mom_growth.png", dpi=150)
    plt.close()
    print("  → Saved: fig_04d_mom_growth.png")

    # ── T-test result ──
    order_level = df_sales.groupby(["invoice", "country"])["revenue"].sum().reset_index()
    order_level.columns = ["invoice", "country", "order_value"]
    uk = order_level[order_level["country"] == "United Kingdom"]["order_value"]
    non_uk = order_level[order_level["country"] != "United Kingdom"]["order_value"]
    t_stat, p_value = stats.ttest_ind(uk, non_uk, equal_var=False)
    print(f"\n  T-test: UK vs Non-UK AOV")
    print(f"    UK mean: £{uk.mean():.2f} (n={len(uk):,})")
    print(f"    Non-UK mean: £{non_uk.mean():.2f} (n={len(non_uk):,})")
    print(f"    t-stat: {t_stat:.4f}, p-value: {p_value:.6f}")
    if p_value < 0.05:
        print(f"    → Reject H₀: Statistically significant difference")
    else:
        print(f"    → Fail to reject H₀")

    # ── OLS Regression ──
    cap_rev = df_sales["revenue"].quantile(0.99)
    cap_qty = df_sales["quantity"].quantile(0.99)
    cap_price = df_sales["price"].quantile(0.99)
    reg_df = df_sales[
        (df_sales["revenue"] <= cap_rev) &
        (df_sales["quantity"] <= cap_qty) &
        (df_sales["price"] <= cap_price)
    ].copy()
    X = sm.add_constant(reg_df[["quantity", "price"]])
    y = reg_df["revenue"]
    model = sm.OLS(y, X).fit()
    print(f"\n  OLS Regression: R² = {model.rsquared:.4f}")
    print(f"    Quantity coeff: {model.params['quantity']:.4f}")
    print(f"    Price coeff:    {model.params['price']:.4f}")

    # ================================================================
    # PHASE 5: Final Summary
    # ================================================================
    print("\n" + "─" * 70)
    print("PHASE 5: Export Manifest")
    print("─" * 70)

    exports = [
        "cleaned_retail.csv", "cleaned_data.csv",
        "kpi_summary.csv", "monthly_kpis.csv", "monthly_trends.csv",
        "country_kpis.csv", "product_kpis.csv",
        "rfm_segments.csv", "customer_summary.csv",
        "tableau_main.csv"
    ]
    for fname in exports:
        fpath = PROCESSED_DIR / fname
        if fpath.exists():
            size_kb = fpath.stat().st_size / 1024
            rows = len(pd.read_csv(fpath))
            print(f"  {fname:<30} {rows:>8,} rows  {size_kb:>10.1f} KB  ✓")
        else:
            print(f"  {fname:<30} NOT FOUND ✗")

    figures = list(REPORTS_DIR.glob("fig_*.png"))
    print(f"\n  Figures generated: {len(figures)}")
    for fig_path in sorted(figures):
        print(f"    {fig_path.name}")

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE — ALL OUTPUTS GENERATED")
    print("=" * 70)


if __name__ == "__main__":
    main()
