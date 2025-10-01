
import sys
import os
import pandas as pd
from datetime import datetime

# ✅ Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.metrics_calculator import (
    load_data,
    calculate_revenue_metrics
)
from calculator.date_utils import get_last_8_weeks, get_last_8_weeks_last_year

# ✅ Load data once to reuse
data = load_data()

def calculate_men_category_revenue(weekly_ranges, year_label):
    """Calculates weekly Gross Revenue for MEN grouped by Category for the given week ranges."""

    weekly_men_category_revenue = []

    for week in weekly_ranges:
        start_date, end_date = week["week_start"], week["week_end"]
        iso_week = week["week_start"].isocalendar()[1]  
        calendar_year = week["week_start"].year  

        print(f"\n📆 Processing {year_label}: Week {iso_week} ({start_date} to {end_date})")

        # ✅ Retrieve revenue metrics
        revenue_metrics = calculate_revenue_metrics(data, start_date, end_date)

        # ✅ Filter only "Online" channel
        df_filtered = data[(data["Date"] >= start_date) & (data["Date"] <= end_date)]
        df_filtered = df_filtered[df_filtered["Sales Channel"] == "Online"]

        # ✅ Ensure required columns exist
        required_columns = ["Gender", "Product Category", "Gross Revenue"]
        missing_columns = [col for col in required_columns if col not in df_filtered.columns]

        if missing_columns:
            raise KeyError(f"❌ Missing columns in dataset: {missing_columns}")

        # ✅ Merge "UNISEX" and missing values into "MEN"
        df_filtered["Gender"] = df_filtered["Gender"].fillna("MEN")
        df_filtered["Gender"] = df_filtered["Gender"].replace(["UNISEX", "-"], "MEN")

        # ✅ Filter ONLY for "MEN"
        df_filtered = df_filtered[df_filtered["Gender"] == "MEN"]

        if df_filtered.empty:
            print(f"⚠️ No data for 'MEN' in Week {iso_week}. Skipping...")
            continue

        # ✅ Standardize category names
        category_mapping = {
            "Poolwear": "Swim & Pool",
            "Swimwear": "Swim & Pool"
        }
        df_filtered["Product Category"] = df_filtered["Product Category"].replace(category_mapping)

        # ✅ Aggregate Gross Revenue by Category for MEN
        revenue_by_category = df_filtered.groupby("Product Category")["Gross Revenue"].sum().reset_index()

        # ✅ Convert values to integers (No conversion to thousands)
        revenue_by_category["Gross Revenue"] = revenue_by_category["Gross Revenue"].round().astype(int)

        # ✅ Log revenue values
        print("\n📊 **Revenue Breakdown by Category for MEN:**")
        print(revenue_by_category)

        for _, row in revenue_by_category.iterrows():
            weekly_men_category_revenue.append({
                "Year Type": year_label,
                "Calendar Year": calendar_year,
                "ISO Week": iso_week,
                "Gender": "MEN",  # ✅ Separate column for Gender
                "Product Category": row["Product Category"],  # ✅ Separate column for Category
                "Value": row["Gross Revenue"]
            })

    return pd.DataFrame(weekly_men_category_revenue)


# ✅ Get last 8 weeks dynamically
last_8_weeks, _ = get_last_8_weeks()
last_8_weeks_last_year, _ = get_last_8_weeks_last_year()

# ✅ Run calculations for both Current Year and Last Year
men_category_revenue_current_year = calculate_men_category_revenue(last_8_weeks, "Current Year")
men_category_revenue_last_year = calculate_men_category_revenue(last_8_weeks_last_year, "Last Year")

# ✅ Merge both years into a single DataFrame
men_category_revenue_final = pd.concat([men_category_revenue_last_year, men_category_revenue_current_year])

if men_category_revenue_final.empty:
    print("\n❌ No revenue data found for MEN & Category. Exiting...")
    sys.exit(1)

# ✅ Sort DataFrame ("Last Year" first)
men_category_revenue_final["Year Type"] = pd.Categorical(
    men_category_revenue_final["Year Type"], categories=["Last Year", "Current Year"], ordered=True
)
# ✅ Sort DataFrame ("Last Year" first)
men_category_revenue_final["Year Type"] = pd.Categorical(
    men_category_revenue_final["Year Type"], categories=["Last Year", "Current Year"], ordered=True
)
men_category_revenue_final = men_category_revenue_final.sort_values(
    by=["Gender", "Product Category", "Year Type"], 
    ascending=[True, True, True]  # ✅ Fixed length
)

# ✅ Define save path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Save as a single file
output_path = os.path.join(OUTPUT_DIR, "men_category_revenue_raw.csv")
men_category_revenue_final.to_csv(output_path, index=False)

print(f"\n✅ Successfully saved MEN Category Revenue data to: {output_path}")

# ✅ Print the entire final dataset
print("\n📊 **Full MEN Category Revenue Dataset:**")
print(men_category_revenue_final.to_string(index=False))