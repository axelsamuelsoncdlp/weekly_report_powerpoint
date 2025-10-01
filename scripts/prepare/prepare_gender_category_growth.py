import sys
import os
import pandas as pd
from datetime import datetime

# ✅ Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.metrics_calculator import load_data
from calculator.date_utils import get_last_8_weeks, get_last_8_weeks_last_year

def load_and_prepare_gender_category_growth():
    """Loads and processes gender-category growth data."""
    data = load_data()
    last_8_weeks, _ = get_last_8_weeks()
    last_8_weeks_last_year, _ = get_last_8_weeks_last_year()

    gender_category_growth_data = calculate_gender_category_growth(data, last_8_weeks, last_8_weeks_last_year)

    if gender_category_growth_data.empty:
        print("\n❌ No growth data found for Gender & Category. Exiting...")
        return

    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output_path = os.path.join(OUTPUT_DIR, "gender_category_growth_raw.csv")
    gender_category_growth_data.to_csv(output_path, index=False)
    print(f"\n✅ Successfully saved Gender & Category Growth data to: {output_path}")
    print("\n📊 **Full Gender & Category Growth Dataset:**")
    print(gender_category_growth_data.to_string(index=False))

def calculate_gender_category_growth(data, weekly_ranges, last_year_ranges):
    """Calculates the growth in Gross Revenue by Gender & Category between Current Year and Last Year."""
    weekly_growth_data = []

    for current_week, last_year_week in zip(weekly_ranges, last_year_ranges):
        start_date, end_date = current_week["week_start"], current_week["week_end"]
        last_year_start, last_year_end = last_year_week["week_start"], last_year_week["week_end"]

        iso_week = current_week["week_start"].isocalendar()[1]  
        calendar_year = current_week["week_start"].year  

        print(f"\n📆 Processing Growth: Week {iso_week} ({start_date} to {end_date}) compared to ({last_year_start} to {last_year_end})")
        print("\n🔍 **Available Columns in Data:**", list(data.columns))

        date_col = next((col for col in data.columns if "date" in col.lower()), None)
        gender_col = next((col for col in data.columns if "gender" in col.lower()), None)
        category_col = next((col for col in data.columns if "category" in col.lower()), None)
        revenue_col = next((col for col in data.columns if "gross revenue (ex" in col.lower()), None)

        if not date_col or not gender_col or not category_col or not revenue_col:
            print("❌ Missing required columns! Skipping this week.")
            continue  

        print(f"✅ Using '{date_col}' as the Date column.")
        print(f"✅ Using '{gender_col}' as the Gender column.")
        print(f"✅ Using '{category_col}' as the Category column.")
        print(f"✅ Using '{revenue_col}' as the Gross Revenue column.")

        current_data = data[(data[date_col] >= start_date) & (data[date_col] <= end_date)]
        last_year_data = data[(data[date_col] >= last_year_start) & (data[date_col] <= last_year_end)]

        current_revenue = (
            current_data.groupby([gender_col, category_col])[revenue_col]
            .sum()
            .reset_index()
        )
        
        last_year_revenue = (
            last_year_data.groupby([gender_col, category_col])[revenue_col]
            .sum()
            .reset_index()
        )

        revenue_comparison = pd.merge(
            current_revenue, 
            last_year_revenue, 
            on=[gender_col, category_col], 
            how="outer", 
            suffixes=("_current", "_last_year")
        ).fillna(0)

        print("\n📊 **Gross Revenue Comparison (Current Year vs Last Year) by Gender & Category:**")
        print(revenue_comparison[[gender_col, category_col, f"{revenue_col}_current", f"{revenue_col}_last_year"]])

        revenue_comparison["Growth (%)"] = (
            ((revenue_comparison[f"{revenue_col}_current"] - revenue_comparison[f"{revenue_col}_last_year"]) / 
            revenue_comparison[f"{revenue_col}_last_year"].replace(0, 1)) * 100
        ).round(1)

        print("\n📊 **Revenue Growth by Gender & Category:**")
        print(revenue_comparison[[gender_col, category_col, "Growth (%)"]])

        for _, row in revenue_comparison.iterrows():
            weekly_growth_data.append({
                "ISO Week": iso_week,
                "Calendar Year": calendar_year,
                "Gender": row[gender_col],
                "Product Category": row[category_col],
                "Current Year Revenue": row[f"{revenue_col}_current"],
                "Last Year Revenue": row[f"{revenue_col}_last_year"],
                "Growth (%)": row["Growth (%)"]
            })

    return pd.DataFrame(weekly_growth_data)
