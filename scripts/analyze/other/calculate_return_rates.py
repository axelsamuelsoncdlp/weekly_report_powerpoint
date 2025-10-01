import sys
import os
import pandas as pd
from tabulate import tabulate

# ✅ Load data
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from calculator.metrics_calculator import load_data

data = load_data()

# ✅ Check required columns
required_columns = {
    "Date", "Gross Revenue (ex. VAT)", "Returns Received",
    "Channel Group", "New/Returning Customer"
}
missing = required_columns - set(data.columns)
if missing:
    raise KeyError(f"❌ Missing columns: {missing}")

# ✅ Prepare date + filter to Online only
data["Date"] = pd.to_datetime(data["Date"])
data["Month"] = data["Date"].dt.to_period("M").astype(str)
data = data[
    (data["Channel Group"] == "Online") &
    data["Gross Revenue (ex. VAT)"].notna() &
    data["Returns Received"].notna() &
    data["New/Returning Customer"].isin(["New", "Returning"])
]

# ✅ Create export directory
output_dir = "/Users/axelsamuelson/Documents/budget_filer"
os.makedirs(output_dir, exist_ok=True)

# ─────────────────────────────────────────────────────────
# ✅ PART 1: Overall Online Return Rate (no customer split)
# ─────────────────────────────────────────────────────────
monthly_total = data.groupby("Month").agg(
    Gross_Revenue=("Gross Revenue (ex. VAT)", "sum"),
    Returns=("Returns Received", "sum")
).reset_index()

monthly_total["Return Rate (%)"] = (monthly_total["Returns"] / monthly_total["Gross_Revenue"] * 100).round(2)

# ✅ Export part 1
monthly_total_path = os.path.join(output_dir, "monthly_return_rates_online.csv")
monthly_total.to_csv(monthly_total_path, index=False)

# ✅ Print in terminal
display_df = monthly_total.copy()
display_df["Gross_Revenue"] = display_df["Gross_Revenue"].round(0).astype(int).apply(lambda x: f"{x:,}")
display_df["Returns"] = display_df["Returns"].round(0).astype(int).apply(lambda x: f"{x:,}")
display_df["Return Rate (%)"] = display_df["Return Rate (%)"].apply(lambda x: f"{x:.1f}%")

print("\n📦 Monthly Return Rates – Online Total")
print(tabulate(display_df, headers="keys", tablefmt="fancy_grid", showindex=False))

# ──────────────────────────────────────────────────────────────
# ✅ PART 2: Split by New vs Returning Customer (Online only)
# ──────────────────────────────────────────────────────────────
monthly_split = data.groupby(["Month", "New/Returning Customer"]).agg(
    Gross_Revenue=("Gross Revenue (ex. VAT)", "sum"),
    Returns=("Returns Received", "sum")
).reset_index()

monthly_split["Return Rate (%)"] = (monthly_split["Returns"] / monthly_split["Gross_Revenue"] * 100).round(2)

# ✅ Export part 2
monthly_split_path = os.path.join(output_dir, "monthly_return_rates_online_by_customer_type.csv")
monthly_split.to_csv(monthly_split_path, index=False)

print(f"\n✅ CSV saved (total): {monthly_total_path}")
print(f"✅ CSV saved (by customer type): {monthly_split_path}")
