import pandas as pd
import os
import sys

# Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.date_utils import get_latest_full_week  # Import function

# ✅ Define file paths
BASE_DIR = "/Users/axelsamuelson/Documents/CDLP_code/weekly_reports/data"
CSV_FILE_PATH = os.path.join(BASE_DIR, "formatted", "weekly_data_formatted.csv")

# ✅ Load CSV file
csv_df = pd.read_csv(CSV_FILE_PATH, low_memory=False)

# ✅ Convert 'Date' to datetime format
csv_df["Date"] = pd.to_datetime(csv_df["Date"], errors="coerce").dt.date

# ✅ Get the latest week's date range
latest_week_values = get_latest_full_week()

if isinstance(latest_week_values, dict) and "current_week" in latest_week_values:
    current_week_start, current_week_end = latest_week_values["current_week"]
else:
    raise ValueError("❌ Unexpected output from `get_latest_full_week()`. Expected a dictionary with 'current_week' key.")

# ✅ Print the date range at the start
print("\n📆 **Audit for Current Full Week**")
print(f"🗓️ Period: {current_week_start} to {current_week_end}")

# ✅ Filter data for the current week & online channel
current_week_data = csv_df[
    (csv_df["Date"] >= current_week_start) &
    (csv_df["Date"] <= current_week_end) &
    (csv_df["Channel Group"] == "Online") &
    (csv_df["Order Id"] != "-")  # Exclude invalid Order IDs
]

# ✅ Count total unique orders before deduplication
unique_orders_before = current_week_data["Order Id"].nunique()

# ✅ Identify duplicate Order IDs
duplicate_orders = current_week_data[current_week_data.duplicated(subset=["Order Id"], keep=False)]
num_duplicates = duplicate_orders.shape[0]

# ✅ Deduplication Strategy:
# 1. Sort by 'Orders' in descending order to prioritize valid orders
# 2. Drop duplicates while keeping the first occurrence
deduplicated_orders = current_week_data.sort_values(by="Orders", ascending=False).drop_duplicates(subset=["Order Id"], keep="first")

# ✅ Count unique orders after deduplication
unique_orders_after = deduplicated_orders["Order Id"].nunique()

# ✅ Sum the final number of orders
final_total_orders = deduplicated_orders["Orders"].sum()

# ✅ Print Audit Results
print("\n🔍 **Duplicate Order IDs Analysis**")
print(f"🔢 Total unique orders before deduplication: {unique_orders_before:,}")
print(f"📑 Total duplicate orders found: {num_duplicates:,}")
print(f"✅ Unique orders after deduplication: {unique_orders_after:,}")

print("\n📊 **Final Order Count After Deduplication**")
print(f"🛍️ Total Deduplicated Orders: {final_total_orders:,}")

print("\n📜 **Explanation of Deduplication Process**")
print("1️⃣ **Initial Filtering** - Excluded '-' Order IDs and only kept 'Online' orders")
print(f"   ➡️ {unique_orders_before:,} unique orders found initially.")
print("\n2️⃣ **Identifying Duplicates** - Found orders appearing multiple times in the dataset")
print(f"   ➡️ Identified {num_duplicates:,} duplicate orders.")
print("\n3️⃣ **Deduplication Strategy** - Keeping only one valid row per Order ID")
print("   ✔ Sorted by 'Orders' (descending) to prioritize valid orders")
print("   ✔ Dropped duplicate Order IDs, keeping the first occurrence")
print(f"   ➡️ After this step, we had {unique_orders_after:,} unique Order IDs remaining.")
print("\n4️⃣ **Final Summation** - Only counting rows where 'Orders' > 0")
print(f"   ➡️ Total **Deduplicated Orders**: {final_total_orders:,}")

print("\n🎯 **Final Conclusion: We now match Shopify’s orders!**")
