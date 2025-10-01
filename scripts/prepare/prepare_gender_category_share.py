import sys
import os
import pandas as pd

# Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.metrics_calculator import (
    load_data,
    calculate_revenue_metrics
)
from calculator.date_utils import get_last_8_weeks

# ✅ Load dataset
data = load_data()

# ✅ Normalize Gender and Category text
data["Gender"] = data["Gender"].str.strip().str.upper()
data["Product Category"] = data["Product Category"].str.strip().str.upper()

# ✅ Log unique categories after normalization
print("\n🔍 Unique Categories after normalization:", data["Product Category"].dropna().unique())


def calculate_category_share_last_8_weeks(gender: str):
    """
    Calculates the share (%) of gross revenue for each category in the last 8 weeks.
    """
    print(f"\n🔍 Calculating category revenue share for {gender}...")  

    # ✅ Retrieve last 8 weeks
    weekly_ranges, _ = get_last_8_weeks()

    # ✅ Extract relevant data for the gender
    # For MEN, include UNISEX, KIDS, and 3 X
    if gender == "MEN":
        gender_data = data[data["Gender"].isin(["MEN", "UNISEX", "KIDS", "3 X"])]
    else:
        gender_data = data[data["Gender"] == gender]

    # ✅ Prepare storage for results
    share_data = []

    # ✅ Iterate over weeks and calculate revenue share
    for week in weekly_ranges:
        start_date, end_date = week["week_start"], week["week_end"]
        iso_week = week["week_start"].isocalendar()[1]  # Extract ISO week number

        print(f"\n📆 Processing week {iso_week} ({start_date} to {end_date})")

        # ✅ Filter data for this week and Online channel only
        week_data = data[(data["Date"] >= start_date) & (data["Date"] <= end_date)]
        week_data = week_data[week_data["Sales Channel"] == "Online"]
        
        # ✅ Apply gender filter with UNISEX/KIDS/3X/NaN merged into MEN
        if gender == "MEN":
            week_gender_data = week_data[
                (week_data["Gender"].isin(["MEN", "UNISEX", "KIDS", "3 X"])) | 
                (week_data["Gender"].isna())
            ]
        else:
            week_gender_data = week_data[week_data["Gender"] == gender]

        # ✅ Calculate total revenue for ALL genders in this week (for SOB denominator)
        total_revenue_all = week_data["Gross Revenue"].sum()

        # ✅ Extract unique categories for this gender
        unique_categories = week_gender_data["Product Category"].dropna().unique()

        # ✅ Calculate share for each category
        for category in unique_categories:
            category_data = week_gender_data[week_gender_data["Product Category"] == category]
            category_revenue = category_data["Gross Revenue"].sum()

            # ✅ Calculate share percentage (category revenue / total revenue for all genders)
            share = (category_revenue / total_revenue_all * 100) if total_revenue_all > 0 else 0

            # ✅ Store the results
            share_data.append({
                "ISO Week": iso_week,
                "Gender": gender.title(),  # Ensure correct capitalization
                "Product Category": category.title(),  # Proper formatting
                "Gross Revenue": round(category_revenue, 2),
                "Total Revenue": round(total_revenue_all, 2),
                "Share (%)": round(share, 0),  # Round to 0 decimal places
            })

        # ✅ Add Total row for this gender (based on actual total revenue for this gender)
        total_gender_revenue = week_gender_data["Gross Revenue"].sum()
        total_gender_share = (total_gender_revenue / total_revenue_all * 100) if total_revenue_all > 0 else 0

        share_data.append({
            "ISO Week": iso_week,
            "Gender": gender.title(),
            "Product Category": "Total",
            "Gross Revenue": round(total_gender_revenue, 2),
            "Total Revenue": round(total_revenue_all, 2),
            "Share (%)": round(total_gender_share, 0),  # Round to 0 decimal places
        })

    return pd.DataFrame(share_data)


# ✅ Run calculations for both Genders
share_men = calculate_category_share_last_8_weeks("MEN")
share_women = calculate_category_share_last_8_weeks("WOMEN")

# ✅ Combine the data
final_share_data = pd.concat([share_men, share_women])

# ✅ Save to a single file
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

output_file = os.path.join(OUTPUT_DIR, "gender_category_share_raw.csv")
final_share_data.to_csv(output_file, index=False)

# ✅ Print confirmation
print(f"\n✅ Gender Category Share data successfully saved to: {output_file}")

# ✅ Preview output
print("\n📊 **Preview of Share Data:**")
print(final_share_data.head(10).to_string(index=False))
