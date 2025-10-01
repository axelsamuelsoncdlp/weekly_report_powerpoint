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

def calculate_women_category_revenue(weekly_ranges, year_label):
    """Calculates weekly Gross Revenue for WOMEN grouped by Category for the given week ranges."""

    weekly_women_category_revenue = []

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

        # ✅ Merge "UNISEX" and missing values into "WOMEN"
        df_filtered["Gender"] = df_filtered["Gender"].fillna("WOMEN")
        df_filtered["Gender"] = df_filtered["Gender"].replace(["UNISEX", "-"], "WOMEN")

        # ✅ Filter ONLY for "WOMEN"
        df_filtered = df_filtered[df_filtered["Gender"] == "WOMEN"]

        if df_filtered.empty:
            print(f"⚠️ No data for 'WOMEN' in Week {iso_week}. Skipping...")
            continue

        # ✅ Standardize category names
        category_mapping = {
            "Poolwear": "Swim & Pool",
            "Swimwear": "Swim & Pool"
        }
        df_filtered["Product Category"] = df_filtered["Product Category"].replace(category_mapping)

        # ✅ Aggregate Gross Revenue by Category for WOMEN
        revenue_by_category = df_filtered.groupby("Product Category")["Gross Revenue"].sum().reset_index()

        # ✅ Convert values to integers
        revenue_by_category["Gross Revenue"] = revenue_by_category["Gross Revenue"].round().astype(int)

        # ✅ Log revenue values
        print("\n📊 **Revenue Breakdown by Category for WOMEN:**")
        print(revenue_by_category)

        for _, row in revenue_by_category.iterrows():
            weekly_women_category_revenue.append({
                "Year Type": year_label,
                "Calendar Year": calendar_year,
                "ISO Week": iso_week,
                "Gender": "WOMEN",
                "Product Category": row["Product Category"],
                "Value": row["Gross Revenue"]
            })

    return pd.DataFrame(weekly_women_category_revenue)


# ✅ Get last 8 weeks dynamically
last_8_weeks, _ = get_last_8_weeks()
last_8_weeks_last_year, _ = get_last_8_weeks_last_year()

# ✅ Run calculations for both Current Year and Last Year
women_category_revenue_current_year = calculate_women_category_revenue(last_8_weeks, "Current Year")
women_category_revenue_last_year = calculate_women_category_revenue(last_8_weeks_last_year, "Last Year")

# ✅ Merge both years into a single DataFrame
women_category_revenue_final = pd.concat([women_category_revenue_last_year, women_category_revenue_current_year])

if women_category_revenue_final.empty:
    print("\n❌ No revenue data found for WOMEN & Category. Exiting...")
    sys.exit(1)

# ✅ Sort DataFrame ("Last Year" first)
women_category_revenue_final["Year Type"] = pd.Categorical(
    women_category_revenue_final["Year Type"], categories=["Last Year", "Current Year"], ordered=True
)
women_category_revenue_final = women_category_revenue_final.sort_values(by=["Gender", "Product Category", "Year Type"], ascending=[True, True, True])

# ✅ Define save path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Save as a single file
output_path = os.path.join(OUTPUT_DIR, "women_category_revenue_raw.csv")
women_category_revenue_final.to_csv(output_path, index=False)

print(f"\n✅ Successfully saved WOMEN Category Revenue data to: {output_path}")

# ✅ Print the entire final dataset
print("\n📊 **Full WOMEN Category Revenue Dataset:**")
print(women_category_revenue_final.to_string(index=False))