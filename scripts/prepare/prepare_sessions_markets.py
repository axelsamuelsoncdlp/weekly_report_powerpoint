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

# ✅ Load real sessions data with country breakdown
def load_sessions_data():
    """Load the updated session_data.csv with country breakdown."""
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    sessions_file = os.path.join(BASE_DIR, "data", "session_data.csv")
    
    sessions_df = pd.read_csv(sessions_file, sep=",", decimal=".")
    sessions_df['Day'] = pd.to_datetime(sessions_df['Day'])
    
    print(f"\n📊 **Loaded Sessions Data:**")
    print(f"  - Total rows: {len(sessions_df)}")
    print(f"  - Date range: {sessions_df['Day'].min()} to {sessions_df['Day'].max()}")
    print(f"  - Unique countries: {sessions_df['Session country'].nunique()}")
    print(f"  - Sample countries: {list(sessions_df['Session country'].dropna().unique()[:10])}")
    
    return sessions_df

sessions_data = load_sessions_data()

def get_sessions_markets():
    """
    Returns the specific markets for sessions data as requested.
    Markets: Total, USA, Sweden, United Kingdom, Germany, Australia, Canada, France, ROW
    """
    # Define the exact markets requested: Total, USA, Sweden, United Kingdom, Germany, Australia, Canada, France, ROW
    markets = [
        "Total",
        "United States",  # USA
        "Sweden", 
        "United Kingdom",
        "Germany",
        "Australia", 
        "Canada",
        "France",
        "ROW"
    ]
    
    print(f"\n📊 **Sessions Markets (Order as specified):**")
    for i, market in enumerate(markets, 1):
        print(f"  {i}. {market}")
    
    return markets

def calculate_session_market_data(weekly_ranges, year_label):
    """Calculates weekly session data for specified markets for a given set of week ranges."""

    weekly_sessions = []
    markets = get_sessions_markets()  # Call once per year_label

    for week in weekly_ranges:
        start_date, end_date = week["week_start"], week["week_end"]
        iso_week = week["week_start"].isocalendar()[1]
        calendar_year = week["week_start"].year

        print(f"\n📆 Processing {year_label}: Week {iso_week} ({start_date} to {end_date})")

        for market in markets:
            # ✅ Get real sessions data from session_data.csv
            if market == "Total":
                # Sum all sessions for this week - convert dates to datetime for comparison
                week_sessions_data = sessions_data[
                    (sessions_data["Day"] >= pd.to_datetime(start_date)) & 
                    (sessions_data["Day"] <= pd.to_datetime(end_date))
                ]
                sessions = int(week_sessions_data["Sessions"].sum())
                print(f"  📊 {market}: {sessions:,} sessions (total from all countries)")
            elif market == "ROW":
                # Sum all countries except the specific ones listed
                specific_markets = ["United States", "Sweden", "United Kingdom", "Germany", "Australia", "Canada", "France"]
                week_sessions_data = sessions_data[
                    (sessions_data["Day"] >= pd.to_datetime(start_date)) & 
                    (sessions_data["Day"] <= pd.to_datetime(end_date)) & 
                    (~sessions_data["Session country"].isin(specific_markets)) &
                    (sessions_data["Session country"].notna())
                ]
                sessions = int(week_sessions_data["Sessions"].sum())
                if sessions > 0:
                    countries_count = week_sessions_data["Session country"].nunique()
                    print(f"  📊 {market}: {sessions:,} sessions (from {countries_count} other countries)")
                else:
                    print(f"  📊 {market}: {sessions:,} sessions (ROW)")
            else:
                # Get sessions for specific country
                country_name = market  # Market names match country names in session data
                week_sessions_data = sessions_data[
                    (sessions_data["Day"] >= pd.to_datetime(start_date)) & 
                    (sessions_data["Day"] <= pd.to_datetime(end_date)) & 
                    (sessions_data["Session country"] == country_name)
                ]
                sessions = int(week_sessions_data["Sessions"].sum()) if not week_sessions_data.empty else 0
                print(f"  📊 {market}: {sessions:,} sessions (real data from sessions_data.csv)")

            # ✅ Append data with "Year Type", "Calendar Year", "ISO Week", "Market", and "Sessions"
            weekly_sessions.append({
                "Year Type": year_label,
                "Calendar Year": calendar_year,
                "ISO Week": iso_week,
                "Market": market,
                "Value": sessions
            })
    
    return pd.DataFrame(weekly_sessions)

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
sessions_current_year = calculate_session_market_data(last_8_weeks, "Current Year")
sessions_last_year = calculate_session_market_data(last_8_weeks_last_year, "Last Year")

# ✅ Merge both years into a single DataFrame
sessions_final = pd.concat([sessions_last_year, sessions_current_year])

# ✅ Assign sorting order based on last 8 weeks order
sessions_final["SortOrder"] = sessions_final.apply(
    lambda row: last_8_weeks_order.index((row["Calendar Year"], row["ISO Week"]))
    if (row["Calendar Year"], row["ISO Week"]) in last_8_weeks_order else float("inf"),
    axis=1
)

# ✅ Ensure correct sorting
sessions_final = sessions_final.sort_values(by="SortOrder").drop(columns=["SortOrder"])

# ✅ Debug before saving
print("\n📊 **Final Sessions Markets DataFrame (First Rows)**")
print(sessions_final[["Year Type", "Calendar Year", "ISO Week", "Market"]].drop_duplicates())

# ✅ Define save path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ Save as a single file
output_path = os.path.join(OUTPUT_DIR, "sessions_markets_raw.csv")
sessions_final.to_csv(output_path, index=False, sep=";", decimal=",")

print(f"\n✅ **Sessions Markets data saved to:** {output_path}")
print(f"📊 **Total rows:** {len(sessions_final)}")
print(f"📊 **Markets:** {sessions_final['Market'].nunique()}")
print(f"📊 **Weeks:** {sessions_final['ISO Week'].nunique()}")
print(f"📊 **Years:** {sessions_final['Year Type'].nunique()}")

