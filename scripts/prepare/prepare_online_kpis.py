import sys
import os
import pandas as pd
from datetime import datetime

# ✅ Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.metrics_calculator import (
    load_data,
    load_spend_data,
    calculate_revenue_metrics,
    calculate_marketing_spend
)
from calculator.orders import deduplicate_orders  # ✅ Import deduplicated order calculation
from calculator.date_utils import get_last_8_weeks, get_last_8_weeks_last_year

# ✅ Load data once to reuse
data = load_data()
spend_data = load_spend_data()

def calculate_kpis(weekly_ranges, year_label):
    """Calculates weekly KPIs for a given set of week ranges and assigns the correct year dynamically."""
    
    weekly_kpis = []

    for week in weekly_ranges:
        start_date, end_date = week["week_start"], week["week_end"]
        iso_week = week["week_start"].isocalendar()[1]  # ✅ Extract actual ISO week number
        calendar_year = week["week_start"].year  # ✅ Extract actual calendar year

        print(f"\n📆 Processing {year_label}: Week {iso_week} ({start_date} to {end_date})")  # ✅ Debugging

        revenue_metrics = calculate_revenue_metrics(data, start_date, end_date)
        new_customers = revenue_metrics.get("New Customers", 0)
        returning_customers = revenue_metrics.get("Returning Customers", 0)
        gross_revenue = revenue_metrics.get("Gross Revenue", 0)
        sessions = revenue_metrics.get("Sessions", 0)
        aov_new = revenue_metrics.get("AOV New Customers (ex. VAT)", 0)
        aov_returning = revenue_metrics.get("AOV Returning Customers (ex. VAT)", 0)

        # ✅ Fix: Ensure orders is returned as a single integer
        orders_df = deduplicate_orders(data, start_date, end_date)
        orders = orders_df.shape[0] if isinstance(orders_df, pd.DataFrame) else int(orders_df)

        # ✅ Ensure values are numeric (handle both Pandas objects and raw numbers)
        sessions = pd.to_numeric(sessions, errors="coerce")
        gross_revenue = pd.to_numeric(gross_revenue, errors="coerce")

        # ✅ Convert to integer if it's a single number (fix for numpy.int64 issue)
        if isinstance(sessions, (int, float)) or pd.notna(sessions):
            sessions = int(sessions)

        if isinstance(gross_revenue, (int, float)) or pd.notna(gross_revenue):
            gross_revenue = float(gross_revenue)

        # ✅ Debugging: Print types to ensure numeric conversion
        print(f"\n📊 Debugging Orders, Sessions & Revenue")
        print(f"🔹 Orders Type: {type(orders)}, Value: {orders}")
        print(f"🔹 Sessions Type: {type(sessions)}, Value: {sessions}")
        print(f"🔹 Gross Revenue Type: {type(gross_revenue)}, Value: {gross_revenue}")

        # ✅ Handle division safely
        conversion_rate = (orders / sessions) * 100 if sessions > 0 else 0

        marketing_spend, cos_percent, ncac = calculate_marketing_spend(
            spend_data, start_date, end_date, gross_revenue, new_customers
        )

        # ✅ Append data with "Year Type", "Calendar Year", and "ISO Week"
        weekly_kpis.append({
            "Year Type": year_label,
            "Calendar Year": calendar_year,  # ✅ Dynamically assigned
            "ISO Week": iso_week,
            "Metric": "Sessions",
            "Value": sessions
        })
        weekly_kpis.append({
            "Year Type": year_label,
            "Calendar Year": calendar_year,
            "ISO Week": iso_week,
            "Metric": "Conversion Rate (%)",
            "Value": conversion_rate
        })
        weekly_kpis.append({
            "Year Type": year_label,
            "Calendar Year": calendar_year,
            "ISO Week": iso_week,
            "Metric": "New Customers",
            "Value": new_customers
        })
        weekly_kpis.append({
            "Year Type": year_label,
            "Calendar Year": calendar_year,
            "ISO Week": iso_week,
            "Metric": "Returning Customers",
            "Value": returning_customers
        })
        weekly_kpis.append({
            "Year Type": year_label,
            "Calendar Year": calendar_year,
            "ISO Week": iso_week,
            "Metric": "AOV New Customers (ex. VAT)",
            "Value": aov_new
        })
        weekly_kpis.append({
            "Year Type": year_label,
            "Calendar Year": calendar_year,
            "ISO Week": iso_week,
            "Metric": "AOV Returning Customers (ex. VAT)",
            "Value": aov_returning
        })
        weekly_kpis.append({
            "Year Type": year_label,
            "Calendar Year": calendar_year,
            "ISO Week": iso_week,
            "Metric": "Online Media Spend",
            "Value": marketing_spend
        })
        weekly_kpis.append({
            "Year Type": year_label,
            "Calendar Year": calendar_year,
            "ISO Week": iso_week,
            "Metric": "nCAC",
            "Value": ncac
        })
        weekly_kpis.append({
            "Year Type": year_label,
            "Calendar Year": calendar_year,
            "ISO Week": iso_week,
            "Metric": "COS%",
            "Value": cos_percent
        })

    return pd.DataFrame(weekly_kpis)

# ✅ Get last 8 weeks dynamically
last_8_weeks, _ = get_last_8_weeks()
last_8_weeks_last_year, _ = get_last_8_weeks_last_year()

# ✅ Define expected order for sorting
last_8_weeks_order = [
    (week["week_start"].year, week["week_start"].isocalendar()[1]) for week in last_8_weeks
]
last_8_weeks_last_year_order = [
    (week["week_start"].year, week["week_start"].isocalendar()[1]) for week in last_8_weeks_last_year
]

print("\n📆 **Expected Current Year Order:**", last_8_weeks_order)
print("\n📆 **Expected Last Year Order:**", last_8_weeks_last_year_order)

# ✅ Run calculations for both Current Year and Last Year
kpis_current_year = calculate_kpis(last_8_weeks, "Current Year")
kpis_last_year = calculate_kpis(last_8_weeks_last_year, "Last Year")

# ✅ Merge both years into a single DataFrame
kpis_final = pd.concat([kpis_last_year, kpis_current_year])

# ✅ Assign sorting order based on last 8 weeks order
kpis_final["SortOrder"] = kpis_final.apply(
    lambda row: last_8_weeks_order.index((row["Calendar Year"], row["ISO Week"]))
    if (row["Calendar Year"], row["ISO Week"]) in last_8_weeks_order else float("inf"),
    axis=1
)

# ✅ Ensure correct sorting
kpis_final = kpis_final.sort_values(by="SortOrder").drop(columns=["SortOrder"])

# ✅ Debug before saving
print("\n📊 **Final Online KPIs DataFrame (First Rows)**")
print(kpis_final[["Year Type", "Calendar Year", "ISO Week", "Metric"]].drop_duplicates())

# ✅ Define save path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Save as a single file
output_path = os.path.join(OUTPUT_DIR, "online_kpis_raw.csv")
kpis_final.to_csv(output_path, index=False)

print(f"\n✅ Successfully saved Online KPIs data to: {output_path}")