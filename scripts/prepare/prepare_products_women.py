import sys
import os
import pandas as pd

# Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.metrics_calculator import load_data, calculate_revenue_metrics
from calculator.date_utils import get_latest_full_week

def filter_women_products():
    """
    Extracts row-level sales data for WOMEN in the latest full ISO week.
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

    # 5️⃣ **Extract WOMEN data from the same dataset used in `calculate_revenue_metrics`**
    df_women = df_filtered[df_filtered["Gender"] == "WOMEN"]

    # ✅ Debugging: Check if WOMEN data exists
    if df_women.empty:
        print(f"⚠️ No WOMEN data found in {start_date} - {end_date}. Exiting...")
        sys.exit(1)

    print(f"📊 **WOMEN Data Shape:** {df_women.shape}")

    # 6️⃣ **Rename columns to match required format**
    if "Gross Revenue (ex. VAT)" in df_women.columns:
        df_women = df_women.rename(columns={"Gross Revenue (ex. VAT)": "Gross Revenue"})

    # 7️⃣ **Keep only required columns**
    required_columns = ["Date", "Gender", "Category", "Product", "Color", "Gross Revenue", "Sales Qty"]
    df_women = df_women[required_columns]

    # 8️⃣ **Summaries for debugging**
    total_revenue = df_women["Gross Revenue"].sum()
    total_sales_qty = df_women["Sales Qty"].sum()
    min_date = df_women["Date"].min()
    max_date = df_women["Date"].max()

    print(f"\n🔎 **Date Range in WOMEN Data:** {min_date} → {max_date}")
    print(f"💰 **Total WOMEN Gross Revenue:** {total_revenue:,.2f}")
    print(f"📦 **Total WOMEN Sales Qty:** {total_sales_qty:,}")

    print("\n✅ **Filtered WOMEN Products Data (First 10 Rows):**")
    print(df_women.head(10))

    # 9️⃣ **Save final dataset**
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw"))
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "products_women_raw.csv")

    df_women.to_csv(output_file, index=False)
    print(f"\n📂 **Saved WOMEN data to:** {output_file}")

    return df_women

if __name__ == "__main__":
    filter_women_products()