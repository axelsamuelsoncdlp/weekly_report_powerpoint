import sys
import os
import pandas as pd
from datetime import datetime

# ✅ Define paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "formatted", "weekly_data_formatted.csv")

# ✅ Ensure data file exists
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"❌ Data file not found: {DATA_PATH}")

# ✅ Load data from CSV
data = pd.read_csv(DATA_PATH)

# ✅ Import utilities
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from calculator.date_utils import get_last_8_weeks

# ✅ Identify relevant columns dynamically
date_col = next((col for col in data.columns if "date" in col.lower()), None)
gender_col = next((col for col in data.columns if "gender" in col.lower()), None)
revenue_col = next((col for col in data.columns if "gross revenue (ex. vat)" in col.lower()), None)

# ✅ Ensure required columns exist
if not all([date_col, gender_col, revenue_col]):
    raise KeyError("❌ Required columns not found! Check dataset structure.")

print("\n🔍 **Available Columns in Data:**", list(data.columns))
print(f"✅ Using '{date_col}' as the Date column.")
print(f"✅ Using '{gender_col}' as the Gender column.")
print(f"✅ Using '{revenue_col}' as the Gross Revenue (ex. VAT) column.")

# ✅ Get last 8 weeks dynamically
last_8_weeks, _ = get_last_8_weeks()

# ✅ Prepare a list to store results
weekly_revenue_men = []

# ✅ Iterate through each week and calculate revenue
for week in last_8_weeks:
    start_date, end_date = week["week_start"], week["week_end"]
    iso_week = week["week_start"].isocalendar()[1]  # ✅ Extract actual ISO week number
    calendar_year = week["week_start"].year  # ✅ Extract actual calendar year

    print(f"\n📆 **Processing Week {iso_week} ({start_date} to {end_date})**")

    # ✅ Filter data for the specific week range
    weekly_data = data[
        (pd.to_datetime(data[date_col]) >= start_date) & (pd.to_datetime(data[date_col]) <= end_date)
    ]

    # ✅ Filter only "Men" transactions
    weekly_men_data = weekly_data[weekly_data[gender_col].str.lower() == "men"]

    # ✅ Sum the total gross revenue for Men
    total_gross_revenue_men = weekly_men_data[revenue_col].sum()

    # ✅ Format the revenue with 1 decimal and thousand separator
    formatted_revenue = f"{total_gross_revenue_men:,.1f}"

    print(f"   💰 Gross Revenue (ex. VAT) for Men in Week {iso_week}: {formatted_revenue}")

    # ✅ Store the results
    weekly_revenue_men.append({
        "Calendar Year": calendar_year,
        "ISO Week": iso_week,
        "Gross Revenue (ex. VAT)": total_gross_revenue_men
    })

# ✅ Convert to DataFrame
df_weekly_revenue_men = pd.DataFrame(weekly_revenue_men)

# ✅ Sort by latest week first
df_weekly_revenue_men = df_weekly_revenue_men.sort_values(by=["Calendar Year", "ISO Week"], ascending=[False, False])

# ✅ Debug before saving
print("\n📊 **Final Weekly Gross Revenue (ex. VAT) for Men**")
print(df_weekly_revenue_men.to_string(index=False))  # ✅ Print entire dataset

# ✅ Save the summary as a CSV file
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "audits")
os.makedirs(OUTPUT_DIR, exist_ok=True)

output_path = os.path.join(OUTPUT_DIR, "men_weekly_revenue.csv")
df_weekly_revenue_men.to_csv(output_path, index=False)

print(f"\n✅ Successfully saved weekly revenue breakdown to: {output_path}")