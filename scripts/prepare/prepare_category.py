import sys
import os
import pandas as pd

# Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.metrics_calculator import (
    load_data,
    calculate_revenue_metrics
)
from calculator.date_utils import get_last_8_weeks, get_last_8_weeks_last_year

# ✅ Load dataset
data = load_data()

# ✅ Function to Calculate Weekly Revenue by Category
def calculate_category_revenue_last_8_weeks():
    """Calculates weekly gross revenue (ex. VAT) for each Category in the last 8 weeks of the current year."""

    print("\n🔍 Fetching last 8 weeks category-based revenue data...")  
    weekly_ranges, _ = get_last_8_weeks()

    category_revenue = []

    for week in weekly_ranges:
        start_date, end_date = week["week_start"], week["week_end"]
        print(f"\n📆 Processing week: {week['week']} ({start_date} to {end_date})")  

        # ✅ Extract unique categories dynamically from the dataset
        unique_categories = data["Product Category"].dropna().unique()

        for category in unique_categories:
            revenue = calculate_revenue_metrics(
                data[data["Product Category"] == category], start_date, end_date
            ).get("Gross Revenue", 0)

            category_revenue.append({
                "ISO Week": week["week_start"].isocalendar()[1],  
                "Product Category": category,
                "Gross Revenue": round(revenue, 2),
            })

    category_revenue_df = pd.DataFrame(category_revenue)
    print("\n📊 **Gross Revenue by Category (Current Year)**")  
    print(category_revenue_df.head(10))  

    return category_revenue_df


# ✅ Function to Calculate Weekly Revenue by Category for Last Year
def calculate_category_revenue_last_8_weeks_last_year():
    """Calculates weekly gross revenue (ex. VAT) for each Category in the last 8 weeks of the previous year."""

    print("\n🔍 Fetching last 8 weeks category-based revenue data for last year...")  
    weekly_ranges, _ = get_last_8_weeks_last_year()

    category_revenue = []

    for week in weekly_ranges:
        start_date, end_date = week["week_start"], week["week_end"]
        print(f"\n📆 Processing week: {week['week']} ({start_date} to {end_date})")  

        # ✅ Extract unique categories dynamically from the dataset
        unique_categories = data["Product Category"].dropna().unique()

        for category in unique_categories:
            revenue = calculate_revenue_metrics(
                data[data["Product Category"] == category], start_date, end_date
            ).get("Gross Revenue", 0)

            category_revenue.append({
                "ISO Week": week["week_start"].isocalendar()[1],  
                "Product Category": category,
                "Gross Revenue": round(revenue, 2),
            })

    category_revenue_df = pd.DataFrame(category_revenue)
    print("\n📊 **Gross Revenue by Category (Last Year)**")  
    print(category_revenue_df.head(10))  

    return category_revenue_df


# ✅ Run calculations for both years
category_revenue_current = calculate_category_revenue_last_8_weeks()
category_revenue_last_year = calculate_category_revenue_last_8_weeks_last_year()

# ✅ Define file paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Save output to CSV
output_file = os.path.join(OUTPUT_DIR, "category_raw.csv")

# ✅ Combine and save
final_category_revenue = pd.concat([category_revenue_current, category_revenue_last_year])
final_category_revenue.to_csv(output_file, index=False)

print(f"\n✅ Category revenue data successfully saved to: {output_file}")
