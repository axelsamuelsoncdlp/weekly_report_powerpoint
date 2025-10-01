import os
import sys
import pandas as pd

# Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import necessary functions
from calculator.metrics_calculator import load_data
from calculator.date_utils import get_last_8_weeks, get_last_8_weeks_last_year

# ✅ Load data
df = load_data()

# ✅ Ensure 'Date' column is in datetime format
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# ✅ Get relevant date ranges
last_8_weeks = get_last_8_weeks()
last_8_weeks_last_year = get_last_8_weeks_last_year()

# ✅ Convert start_date and end_date to pandas.Timestamp
start_date = pd.Timestamp(last_8_weeks[1]["start"])
end_date = pd.Timestamp(last_8_weeks[1]["end"])
start_date_last_year = pd.Timestamp(last_8_weeks_last_year[1]["start"])
end_date_last_year = pd.Timestamp(last_8_weeks_last_year[1]["end"])

# ✅ Debugging: Print extracted dates
print(f"\n📅 **Date range for last 8 weeks:** {start_date} - {end_date}")
print(f"📅 **Date range for last 8 weeks last year:** {start_date_last_year} - {end_date_last_year}")

# ✅ Filter data for the last 8 weeks and include only WOMEN
df_recent = df[(df["Date"] >= start_date) & (df["Date"] <= end_date) & (df["Gender"] == "WOMEN")]
df_last_year = df[(df["Date"] >= start_date_last_year) & (df["Date"] <= end_date_last_year) & (df["Gender"] == "WOMEN")]

# ✅ Function to check presence of categories for WOMEN
def check_category_presence(df, category):
    return category in df["Category"].unique()

# ✅ Check for SWIMWEAR and POOLWEAR within WOMEN
categories = ["SWIMWEAR", "POOLWEAR"]
results = {}

for category in categories:
    results[category] = {
        "Last 8 Weeks": check_category_presence(df_recent, category),
        "Last 8 Weeks Last Year": check_category_presence(df_last_year, category),
    }

# ✅ Print results
print("\n📊 **Audit Results for SWIMWEAR and POOLWEAR (WOMEN Only)**")
for category, data in results.items():
    print(f"\n🔍 {category}:")
    print(f" - Last 8 Weeks: {'✅ Data Found' if data['Last 8 Weeks'] else '❌ No Data'}")
    print(f" - Last 8 Weeks Last Year: {'✅ Data Found' if data['Last 8 Weeks Last Year'] else '❌ No Data'}")