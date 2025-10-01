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

def calculate_gender_revenue(weekly_ranges, year_label):
    """Calculates weekly Gross Revenue grouped by Gender for the given week ranges."""

    weekly_gender_revenue = []

    for week in weekly_ranges:
        start_date, end_date = week["week_start"], week["week_end"]
        iso_week = week["week_start"].isocalendar()[1]  # ✅ Extract actual ISO week number
        calendar_year = week["week_start"].year  # ✅ Extract actual calendar year

        print(f"\n📆 Processing {year_label}: Week {iso_week} ({start_date} to {end_date})")  # ✅ Debugging

        # ✅ Hämta den filtrerade datan från calculate_revenue_metrics
        revenue_metrics = calculate_revenue_metrics(data, start_date, end_date)

        # ✅ Filtrera endast "Online" data från den fullständiga datan
        df_filtered = data[(data["Date"] >= start_date) & (data["Date"] <= end_date)]
        df_filtered = df_filtered[df_filtered["Channel Group"] == "Online"]

        # ✅ Kontrollera att de nödvändiga kolumnerna finns
        required_columns = ["Gender", "Gross Revenue (ex. VAT)"]
        missing_columns = [col for col in required_columns if col not in df_filtered.columns]

        if missing_columns:
            raise KeyError(f"❌ Följande kolumner saknas i datasetet: {missing_columns}")

        # ✅ Hantera UNISEX, "-" och saknade värden (läggs till i MEN)
        df_filtered["Gender"] = df_filtered["Gender"].fillna("MEN")  # Lägg till saknade rader i MEN
        df_filtered["Gender"] = df_filtered["Gender"].replace(["UNISEX", "-"], "MEN")  # Lägg ihop UNISEX och "-" med MEN

        # ✅ Summera Gross Revenue per kön
        revenue_by_gender = df_filtered.groupby("Gender")["Gross Revenue (ex. VAT)"].sum().reset_index()

        # ✅ Omvandla värden till heltal
        revenue_by_gender["Gross Revenue (ex. VAT)"] = revenue_by_gender["Gross Revenue (ex. VAT)"].round().astype(int)

        # ✅ Se till att både "MEN" & "WOMEN" kategorier finns
        revenue_dict = revenue_by_gender.set_index("Gender")["Gross Revenue (ex. VAT)"].to_dict()
        gross_revenue_men = revenue_dict.get("MEN", 0)
        gross_revenue_women = revenue_dict.get("WOMEN", 0)

        # ✅ Log revenue values
        print(f"   🔹 MEN Revenue (inkl. UNISEX, '-' & saknade värden): {gross_revenue_men}")
        print(f"   🔹 WOMEN Revenue: {gross_revenue_women}")

        weekly_gender_revenue.append({
            "Year Type": year_label,
            "Calendar Year": calendar_year,  # ✅ Dynamically assigned
            "ISO Week": iso_week,
            "Metric": "Gross Revenue - MEN",
            "Value": gross_revenue_men
        })
        weekly_gender_revenue.append({
            "Year Type": year_label,
            "Calendar Year": calendar_year,
            "ISO Week": iso_week,
            "Metric": "Gross Revenue - WOMEN",
            "Value": gross_revenue_women
        })

    return pd.DataFrame(weekly_gender_revenue)


# ✅ Get last 8 weeks dynamically
last_8_weeks, _ = get_last_8_weeks()
last_8_weeks_last_year, _ = get_last_8_weeks_last_year()

# ✅ Run calculations for both Current Year and Last Year
gender_revenue_current_year = calculate_gender_revenue(last_8_weeks, "Current Year")
gender_revenue_last_year = calculate_gender_revenue(last_8_weeks_last_year, "Last Year")

# ✅ Merge both years into a single DataFrame
gender_revenue_final = pd.concat([gender_revenue_last_year, gender_revenue_current_year])

# ✅ Define expected order for sorting
last_8_weeks_order = [
    (week["week_start"].year, week["week_start"].isocalendar()[1]) for week in last_8_weeks
]
last_8_weeks_last_year_order = [
    (week["week_start"].year, week["week_start"].isocalendar()[1]) for week in last_8_weeks_last_year
]

# ✅ Assign sorting order based on last 8 weeks order
gender_revenue_final["SortOrder"] = gender_revenue_final.apply(
    lambda row: last_8_weeks_order.index((row["Calendar Year"], row["ISO Week"]))
    if (row["Calendar Year"], row["ISO Week"]) in last_8_weeks_order else float("inf"),
    axis=1
)

# ✅ Ensure correct sorting
gender_revenue_final = gender_revenue_final.sort_values(by="SortOrder").drop(columns=["SortOrder"])

# ✅ Debug before saving
print("\n📊 **Final Gender Revenue DataFrame (First Rows)**")
print(gender_revenue_final.head(10))  # ✅ Print first few rows including values

# ✅ Define save path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Save as a single file
output_path = os.path.join(OUTPUT_DIR, "gender_revenue_raw.csv")
gender_revenue_final.to_csv(output_path, index=False)

print(f"\n✅ Successfully saved Gender Revenue data to: {output_path}")

# ✅ Print the entire final dataset
print("\n📊 **Full Gender Revenue Dataset:**")
print(gender_revenue_final.to_string(index=False))  # ✅ Print entire dataset for verification