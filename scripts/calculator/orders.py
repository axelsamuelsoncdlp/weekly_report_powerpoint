import pandas as pd
import os
import sys

# Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.date_utils import get_latest_full_week  # Import function

# ✅ Define file paths
BASE_DIR = "/Users/axelsamuelson/Documents/CDLP_CODE/weekly_reports_powerpoint"
CSV_FILE_PATH = os.path.join(BASE_DIR, "data", "formatted", "weekly_data_formatted.csv")

def deduplicate_orders(df, start_date, end_date):
    """Removes duplicate orders and returns a cleaned dataset instead of just an integer."""

    # ✅ Filter data for the selected week & online channel
    filtered_df = df[
        (df["Date"] >= start_date) &
        (df["Date"] <= end_date) &
        (df["Sales Channel"] == "Online") &
        (df["Order No"] != "-")  # Exclude invalid Order IDs
    ]

    # ✅ Identify duplicate Order IDs
    duplicate_orders = filtered_df[filtered_df.duplicated(subset=["Order No"], keep=False)]
    num_duplicates = duplicate_orders.shape[0]

    # ✅ Deduplication Strategy:
    # 1. Sort by 'Sales Qty' in descending order to prioritize valid orders
    # 2. Drop duplicates while keeping the first occurrence
    deduplicated_orders = filtered_df.sort_values(by="Sales Qty", ascending=False).drop_duplicates(subset=["Order No"], keep="first")

    # ✅ Log duplicate findings
    print(f"\n🔍 **Duplicate Order Analysis**")
    print(f"   - Original Orders: {filtered_df.shape[0]}")
    print(f"   - Duplicate Orders Found: {num_duplicates}")
    print(f"   - Final Orders After Deduplication: {deduplicated_orders.shape[0]}")

    # ✅ Return the cleaned DataFrame instead of a count
    return deduplicated_orders

# ✅ Allow standalone execution for debugging
if __name__ == "__main__":
    unique_orders = deduplicate_orders()