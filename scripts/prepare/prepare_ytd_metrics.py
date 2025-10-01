import sys
import os
import pandas as pd
from datetime import datetime

# Ensure the scripts folder is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import necessary modules
from calculator.metrics_calculator import load_data, load_spend_data, calculate_revenue_metrics, calculate_marketing_spend
from calculator.date_utils import get_ytd_time_periods, get_latest_sunday

# Define output file path
RAW_YTD_METRICS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw/ytd_metrics_raw.csv"))

# Define required metric names
METRIC_NAMES = {
    "Gross Revenue": "Online Gross Revenue",
    "Net Revenue": "Online Net Revenue",
    "Returns": "Returns",
    "Return Rate": "Return rate %",
    "Retail Concept Store": "Retail Concept Store",
    "Retail Pop-ups": "Retail Pop-ups, Outlets",
    "Retail Net Revenue": "Retail Net Revenue",
    "Wholesale Net Revenue": "Wholesale Net Revenue",
    "Total Net Revenue": "Total Net Revenue",
    "New Customers": "New Customers",
    "Returning Customers": "Returning Customers",
    "Marketing Spend": "Marketing Spend",
    "Online Cost of Sale %": "Online Cost of Sale (CoS)",
}

# Define required column order
COLUMN_ORDER = ["ytd_current_month", "ytd_last_year", "ytd_two_years", "Budget(1)"]

def clean_value(value):
    """
    Cleans numerical values:
    - Replaces 0, "N/A", "n/m", "N/M" with "-"
    - Converts valid numbers to floats
    """
    if pd.isna(value) or str(value).strip().lower() in ["n/a", "n/m", "n.m", "0"]:
        return "-"
    try:
        return float(value)  # Ensure numeric values remain numbers
    except ValueError:
        return value  # Return as-is if not convertible

def load_and_prepare_ytd_data():
    """Computes Fiscal YTD revenue & cost metrics for Current Year, Last Year, and Two Years Ago."""

    # Load formatted data
    df = load_data()
    spend_df = load_spend_data()

    # Get YTD time periods
    ytd_periods = get_ytd_time_periods()

    # Debugging: Print the Fiscal YTD Date Ranges
    print("\n📅 **Fiscal YTD Date Ranges:**")
    for period, (start, end) in ytd_periods.items():
        print(f"🔹 {period.replace('_', ' ').title()}: {start} → {end}")

    # Initialize dictionary for storing metrics
    metrics = {metric: {} for metric in METRIC_NAMES.values()}

    # Compute revenue metrics for each YTD period
    for period_name, (start_date, end_date) in ytd_periods.items():
        revenue_data = calculate_revenue_metrics(df, start_date, end_date)

        # Debugging: Print revenue data for this period
        print(f"\n🔍 Debug: Revenue Data for {period_name}")
        print(revenue_data)

        spend, cost_of_sale, ncac = calculate_marketing_spend(
            spend_df, start_date, end_date, revenue_data.get("Gross Revenue", 0), revenue_data.get("New Customers", 0)
        )

        for raw_metric, formatted_metric in METRIC_NAMES.items():
            metrics[formatted_metric][period_name] = clean_value(revenue_data.get(raw_metric, "-"))

        # Store Marketing Spend & Cost of Sale correctly
        metrics["Marketing Spend"][period_name] = clean_value(spend)
        metrics["Online Cost of Sale (CoS)"][period_name] = clean_value(cost_of_sale)

    # Convert to DataFrame
    metrics_df = pd.DataFrame.from_dict(metrics, orient="index")

    # Ensure "Budget(1)" column exists and add it if missing
    if "Budget(1)" not in metrics_df.columns:
        metrics_df["Budget(1)"] = "-"

    # Reorder columns
    metrics_df = metrics_df[COLUMN_ORDER]

    # Debugging: Check the final formatted DataFrame
    print("\n✅ **Final YTD Metrics Before Saving:**")
    print(metrics_df)

    # Ensure output directory exists before saving
    os.makedirs(os.path.dirname(RAW_YTD_METRICS_PATH), exist_ok=True)

    # Save YTD metrics
    metrics_df.to_csv(RAW_YTD_METRICS_PATH, index=True)

    print(f"\n✅ Fiscal YTD Metrics saved to `{RAW_YTD_METRICS_PATH}`")

if __name__ == "__main__":
    load_and_prepare_ytd_data()
