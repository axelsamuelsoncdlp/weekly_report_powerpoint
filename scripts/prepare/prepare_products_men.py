import sys
import os
import pandas as pd

# Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.metrics_calculator import load_data, calculate_revenue_metrics
from calculator.date_utils import get_latest_full_week

def filter_men_products():
    """
    Extracts row-level sales data for MEN in the latest full ISO week.
    Ensures that it matches the filtered dataset used in `calculate_revenue_metrics`.
    """

    # 1️⃣ **Load main dataset**
    data = load_data()

    print(f"\n📊 **Loaded Data Shape:** {data.shape}")
    print(f"🔍 **Data Columns:** {list(data.columns)}")

    # 2️⃣ **Get current week's start & end dates**
    latest_week_info = get_latest_full_week()
    if "current_week" not in latest_week_info:
        raise ValueError(
            f"❌ `get_latest_full_week()` did not return expected structure. Got: {latest_week_info}"
        )

    start_date, end_date = latest_week_info["current_week"]
    print(f"\n📆 **Using Date Range:** {start_date} → {end_date}")

    # 3️⃣ **Pre-filter dataset for correct date range + Online channel**
    df_filtered = data[
        (data["Date"] >= start_date) &
        (data["Date"] <= end_date) &
        (data["Channel Group"] == "Online")  # ✅ Match `calculate_revenue_metrics` logic
    ]

    # ✅ Debugging: Check if we have data before passing to metrics
    if df_filtered.empty:
        print(f"⚠️ No Online sales data found for {start_date} - {end_date}. Exiting...")
        sys.exit(1)

    print(f"📊 **Pre-filtered Data for Online Sales:** {df_filtered.shape}")

    # 4️⃣ **Run `calculate_revenue_metrics` on pre-filtered dataset**
    revenue_metrics = calculate_revenue_metrics(df_filtered, start_date, end_date)
    print(f"\n🔎 **Revenue Metrics Summary:** {revenue_metrics}")

    # 5️⃣ **Extract MEN data from the same dataset used in `calculate_revenue_metrics`**
    df_men = df_filtered[df_filtered["Gender"] == "MEN"]

    # ✅ Debugging: Check if MEN data exists
    if df_men.empty:
        print(f"⚠️ No MEN data found in {start_date} - {end_date}. Exiting...")
        sys.exit(1)

    print(f"📊 **MEN Data Shape:** {df_men.shape}")

    # 6️⃣ **Rename columns to match required format**
    if "Gross Revenue (ex. VAT)" in df_men.columns:
        df_men = df_men.rename(columns={"Gross Revenue (ex. VAT)": "Gross Revenue"})

    # 7️⃣ **Keep only required columns**
    required_columns = ["Date", "Gender", "Category", "Product", "Color", "Gross Revenue", "Sales Qty"]
    df_men = df_men[required_columns]

    # 8️⃣ **Summaries for debugging**
    total_revenue = df_men["Gross Revenue"].sum()
    total_sales_qty = df_men["Sales Qty"].sum()
    min_date = df_men["Date"].min()
    max_date = df_men["Date"].max()

    print(f"\n🔎 **Date Range in MEN Data:** {min_date} → {max_date}")
    print(f"💰 **Total MEN Gross Revenue:** {total_revenue:,.2f}")
    print(f"📦 **Total MEN Sales Qty:** {total_sales_qty:,}")

    print("\n✅ **Filtered MEN Products Data (First 10 Rows):**")
    print(df_men.head(10))

    # 9️⃣ **Save final dataset**
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw"))
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "products_men_raw.csv")

    df_men.to_csv(output_file, index=False)
    print(f"\n📂 **Saved MEN data to:** {output_file}")

    return df_men

if __name__ == "__main__":
    filter_men_products()