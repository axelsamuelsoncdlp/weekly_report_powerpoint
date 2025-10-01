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
from calculator.date_utils import get_last_8_weeks, get_last_8_weeks_last_year

# ✅ Load data once to reuse
data = load_data()
spend_data = load_spend_data()

# ✅ Load GM2 values from the CSV file
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GM2_FILE = os.path.join(BASE_DIR, "data", "gm2.csv")

# ✅ Ensure GM2 file exists
if not os.path.exists(GM2_FILE):
    raise FileNotFoundError(f"❌ GM2 file not found: {GM2_FILE}")

# ✅ Load GM2 data with semicolon separator
gm2_df = pd.read_csv(GM2_FILE, sep=';')

# ✅ Extract week number from "Week X, YYYY" format and convert to ISO week
def extract_week_number(week_str):
    """Extract week number from 'Week X, YYYY' format"""
    return int(week_str.split()[1].rstrip(','))

# ✅ Create ISO Week column and extract GM2 values
gm2_df['ISO Week'] = gm2_df['Weeks'].apply(extract_week_number)
gm2_df['GM2'] = gm2_df['Gross margin 2 - Dema MTA'].astype(float)

print("\n📊 **Loaded GM2 Data (First Rows):**")
print(gm2_df.head())


def calculate_contribution(weekly_ranges, year_label):
    """Calculates Contribution for New & Returning Customers and Total Contribution."""
    
    weekly_contributions = []

    for week in weekly_ranges:
        start_date, end_date = week["week_start"], week["week_end"]
        iso_week = week["week_start"].isocalendar()[1]  
        calendar_year = week["week_start"].year  

        # ✅ Fetch GM2 value for the correct year and ISO week
        gm2_row = gm2_df[(gm2_df["Years"] == calendar_year) & (gm2_df["ISO Week"] == iso_week)]
        if gm2_row.empty:
            print(f"⚠️ No GM2 value found for {calendar_year} - Week {iso_week}. Skipping...")
            continue
        gm2_value = gm2_row["GM2"].values[0]

        print(f"\n📆 Processing {year_label}: Week {iso_week} ({start_date} to {end_date}) | GM2: {gm2_value}")

        # ✅ Get revenue metrics
        revenue_metrics = calculate_revenue_metrics(data, start_date, end_date)
        gross_revenue_new = revenue_metrics.get("Gross Revenue (ex. VAT) - New Customers", 0)
        gross_revenue_returning = revenue_metrics.get("Gross Revenue (ex. VAT) - Returning Customers", 0)
        new_customers = revenue_metrics.get("New Customers", 0)
        returning_customers = revenue_metrics.get("Returning Customers", 0)
        new_aov = revenue_metrics.get("AOV New Customers (ex. VAT)", 0)
        returning_aov = revenue_metrics.get("AOV Returning Customers (ex. VAT)", 0)

        # ✅ Calculate total marketing spend
        marketing_spend = calculate_marketing_spend(spend_data, start_date, end_date, 
                                                    revenue_metrics["Gross Revenue"], 
                                                    new_customers)

        # ✅ If marketing_spend is a tuple, extract the first value
        if isinstance(marketing_spend, tuple):
            marketing_spend = marketing_spend[0]

        # ✅ Ensure marketing_spend is a float
        marketing_spend = float(marketing_spend)

        # ✅ Calculate CAC for new and returning customers
        new_CAC = (0.7 * marketing_spend) / new_customers if new_customers > 0 else 0
        returning_CAC = (0.3 * marketing_spend) / returning_customers if returning_customers > 0 else 0

        # ✅ Updated Contribution calculations
        new_customer_contribution = (gm2_value * new_aov - new_CAC) * new_customers
        returning_customer_contribution = (gm2_value * returning_aov - returning_CAC) * returning_customers
        total_contribution = new_customer_contribution + returning_customer_contribution

        print(f"📊 **Example Calculation for Week {iso_week}:**")
        print(f"   🟢 GM2: {gm2_value}")
        print(f"   🟢 Marketing Spend: {marketing_spend}")
        print(f"   🟢 New CAC: {new_CAC}")
        print(f"   🟢 Returning CAC: {returning_CAC}")
        print(f"   🟢 New Contribution: {new_customer_contribution}")
        print(f"   🟢 Returning Contribution: {returning_customer_contribution}")
        print(f"   🟢 Total Contribution: {total_contribution}")

        # ✅ Append data with "Metric" and "Customer Type" columns
        for metric, customer_type, value in [
            ("Gross Revenue", "New Customers", gross_revenue_new),
            ("Gross Revenue", "Returning Customers", gross_revenue_returning),
            ("Contribution", "New Customers", round(new_customer_contribution, 2)),
            ("Contribution", "Returning Customers", round(returning_customer_contribution, 2)),
            ("Contribution", "Total", round(total_contribution, 2))
        ]:
            weekly_contributions.append({
                "Year Type": year_label,
                "Calendar Year": calendar_year,
                "ISO Week": iso_week,
                "Metric": metric,
                "Customer Type": customer_type,
                "Value": value
            })

    return pd.DataFrame(weekly_contributions)


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
contribution_current_year = calculate_contribution(last_8_weeks, "Current Year")
contribution_last_year = calculate_contribution(last_8_weeks_last_year, "Last Year")

# ✅ Merge both years into a single DataFrame
contribution_final = pd.concat([contribution_last_year, contribution_current_year])

# ✅ Assign sorting order based on last 8 weeks order
contribution_final["SortOrder"] = contribution_final.apply(
    lambda row: last_8_weeks_order.index((row["Calendar Year"], row["ISO Week"]))
    if (row["Calendar Year"], row["ISO Week"]) in last_8_weeks_order else float("inf"),
    axis=1
)

# ✅ Ensure correct sorting
contribution_final = contribution_final.sort_values(by="SortOrder").drop(columns=["SortOrder"])

# ✅ Debug before saving
print("\n📊 **Final Contribution DataFrame (First Rows)**")
print(contribution_final[["Year Type", "Calendar Year", "ISO Week", "Metric", "Customer Type"]].drop_duplicates())

# ✅ Define save path
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Save as a single file
output_path = os.path.join(OUTPUT_DIR, "contribution_raw.csv")
contribution_final.to_csv(output_path, index=False)

print(f"\n✅ Successfully saved Contribution data to: {output_path}")