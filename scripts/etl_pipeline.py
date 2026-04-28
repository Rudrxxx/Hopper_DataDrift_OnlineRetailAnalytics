"""
ETL Pipeline — Online Retail II
DVA_B1_T3 | Newton School of Technology
Capstone 2: Data Visualization & Analytics

All cleaning logic is modularized here and called from notebooks/02_cleaning.ipynb.
Every function is documented so any team member can explain it during viva.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Step 1 — Column normalization
# ---------------------------------------------------------------------------

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert column names to clean snake_case."""
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    log.info("Step 1 | Columns normalized: %s", list(df.columns))
    return df


# ---------------------------------------------------------------------------
# Step 2 — Duplicate removal
# ---------------------------------------------------------------------------

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop exact duplicate rows and reset index."""
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    log.info("Step 2 | Duplicates removed: %d rows dropped", before - len(df))
    return df


# ---------------------------------------------------------------------------
# Step 3 — Parse and enrich dates
# ---------------------------------------------------------------------------

def parse_dates(df: pd.DataFrame, date_col: str = "invoicedate") -> pd.DataFrame:
    """
    Parse the invoice date column to datetime.
    Derive: year, month, month_name, day_of_week, hour, quarter.
    These are essential for time-series KPIs and Tableau filters.
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    df["year"]         = df[date_col].dt.year
    df["month"]        = df[date_col].dt.month
    df["month_name"]   = df[date_col].dt.strftime("%B")
    df["quarter"]      = df[date_col].dt.quarter
    df["day_of_week"]  = df[date_col].dt.day_name()
    df["hour"]         = df[date_col].dt.hour

    null_dates = df[date_col].isna().sum()
    log.info("Step 3 | Dates parsed. Null dates: %d", null_dates)
    return df


# ---------------------------------------------------------------------------
# Step 4 — Flag and isolate cancellations
# ---------------------------------------------------------------------------

def flag_cancellations(df: pd.DataFrame, invoice_col: str = "invoice") -> pd.DataFrame:
    """
    Cancelled orders have Invoice starting with 'C'.
    We keep them as a separate flag rather than dropping — they are
    analytically valuable for cancellation rate KPI.
    """
    df = df.copy()
    df["is_cancelled"] = df[invoice_col].astype(str).str.startswith("C")
    cancelled = df["is_cancelled"].sum()
    log.info("Step 4 | Cancellations flagged: %d rows", cancelled)
    return df


# ---------------------------------------------------------------------------
# Step 5 — Remove invalid quantities and prices (non-cancelled only)
# ---------------------------------------------------------------------------

def remove_invalid_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    For non-cancelled rows: drop records with Quantity <= 0 or Price <= 0.
    Cancelled rows may legitimately have negative quantities — retain them.
    Rationale: zero/negative price is a data error, not a business event.
    """
    before = len(df)
    valid_mask = df["is_cancelled"] | ((df["quantity"] > 0) & (df["price"] > 0))
    df = df[valid_mask].reset_index(drop=True)
    log.info("Step 5 | Invalid transactions removed: %d rows", before - len(df))
    return df


# ---------------------------------------------------------------------------
# Step 6 — Handle missing Customer IDs
# ---------------------------------------------------------------------------

def handle_missing_customers(df: pd.DataFrame, customer_col: str = "customer_id") -> pd.DataFrame:
    """
    Missing Customer IDs represent guest/anonymous transactions.
    Strategy: fill with 'GUEST' so they are retained in revenue analysis
    but excluded from customer-level RFM segmentation.
    """
    missing = df[customer_col].isna().sum()
    df = df.copy()
    df[customer_col] = df[customer_col].fillna("GUEST").astype(str).str.strip()
    # Remove trailing .0 from float-cast IDs
    df[customer_col] = df[customer_col].str.replace(r"\.0$", "", regex=True)
    log.info("Step 6 | Missing Customer IDs filled with GUEST: %d rows", missing)
    return df


# ---------------------------------------------------------------------------
# Step 7 — Standardize text columns
# ---------------------------------------------------------------------------

def standardize_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strip whitespace and title-case Description.
    Strip and title-case Country.
    Remove obvious noise values from Description.
    """
    df = df.copy()
    noise = {"?", "??", "???", "DOTCOM POSTAGE", "POSTAGE", "MANUAL",
             "BANK CHARGES", "PACKING CHARGE", "AMAZON FEE"}

    if "description" in df.columns:
        df["description"] = df["description"].astype(str).str.strip().str.title()
        df = df[~df["description"].isin(noise)].reset_index(drop=True)

    if "country" in df.columns:
        df["country"] = df["country"].astype(str).str.strip().str.title()

    log.info("Step 7 | Text columns standardized.")
    return df


# ---------------------------------------------------------------------------
# Step 8 — Derive revenue column
# ---------------------------------------------------------------------------

def derive_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Revenue = Quantity × Price.
    For cancelled rows, revenue will be negative (correct — represents refund value).
    Also derive abs_revenue for magnitude comparisons.
    """
    df = df.copy()
    df["revenue"]     = df["quantity"] * df["price"]
    df["abs_revenue"] = df["revenue"].abs()
    log.info("Step 8 | Revenue derived. Total gross revenue: £{:,.2f}".format(
        df.loc[~df["is_cancelled"], "revenue"].sum()
    ))
    return df


# ---------------------------------------------------------------------------
# Step 9 — Derive product category (first meaningful word of Description)
# ---------------------------------------------------------------------------

def derive_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the first word of Description as a proxy product category.
    Used as a Tableau filter dimension.
    """
    df = df.copy()
    df["category"] = df["description"].astype(str).str.split().str[0]
    log.info("Step 9 | Category column derived. Unique categories: %d", df["category"].nunique())
    return df


# ---------------------------------------------------------------------------
# Master pipeline
# ---------------------------------------------------------------------------

def run_full_pipeline(raw_path: Path) -> pd.DataFrame:
    """
    Execute all cleaning steps in order.
    Returns the fully cleaned and enriched DataFrame.
    """
    log.info("=== ETL PIPELINE START ===")
    log.info("Loading raw data from: %s", raw_path)

    try:
        df = pd.read_csv(raw_path, encoding="ISO-8859-1")
    except UnicodeDecodeError:
        df = pd.read_csv(raw_path, encoding="latin-1")

    log.info("Raw shape: %s", df.shape)

    df = normalize_columns(df)
    df = remove_duplicates(df)
    df = parse_dates(df)
    df = flag_cancellations(df)
    df = remove_invalid_transactions(df)
    df = handle_missing_customers(df)
    df = standardize_text(df)
    df = derive_revenue(df)
    df = derive_category(df)

    log.info("=== ETL PIPELINE COMPLETE ===")
    log.info("Cleaned shape: %s", df.shape)
    return df


def save_processed(df: pd.DataFrame, output_path: Path) -> None:
    """Write the cleaned DataFrame to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    log.info("Saved to: %s", output_path)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    cleaned = run_full_pipeline(args.input)
    save_processed(cleaned, args.output)

