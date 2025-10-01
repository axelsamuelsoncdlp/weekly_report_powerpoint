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

def get_top_8_markets():
    """
    Gets the top 8 markets based on revenue from the latest week.
    """
    weeks_list, _ = get_last_8_weeks()
    latest_week = max(weeks_list, key=lambda x: x["week_start"])
    start, end = latest_week["week_start"], latest_week["week_end"]

    # ✅ Aggregate revenue by market for the latest week
    market_revenue = {}
    for market in data["Country"].unique():
        if pd.isna(market):  # Skip NaN values
            continue
        market_df = data[(data["Country"] == market) & (data["Date"] >= start) & (data["Date"] <= end)]
        if not market_df.empty:
            revenue_data = calculate_revenue_metrics(market_df, start, end)
            revenue = revenue_data.get("Gross Revenue", 0)
            # Ensure revenue is numeric
            if pd.isna(revenue):
                revenue = 0
            market_revenue[market] = float(revenue)

    # ✅ Sort markets by revenue and get the top 8
    sorted_markets = sorted(market_revenue.items(), key=lambda x: x[1], reverse=True)
    top_8_markets = [market for market, _ in sorted_markets[:8]]

    print(f"\n📊 **Top 8 Markets by Revenue (Week {latest_week['week_start'].isocalendar()[1]}):**")
    for i, (market, revenue) in enumerate(sorted_markets[:8], 1):
        print(f"  {i}. {market}: {revenue:,.0f} SEK")

    return top_8_markets

def calculate_session_market_data(weekly_ranges, year_label):
    """Calculates weekly session data for top 8 markets for a given set of week ranges."""

    weekly_sessions = []
    top_8_markets = get_top_8_markets()  # Call once per year_label

    for week in weekly_ranges:
        start_date, end_date = week["week_start"], week["week_end"]
        iso_week = week["week_start"].isocalendar()[1]
        calendar_year = week["week_start"].year

        print(f"\n📆 Processing {year_label}: Week {iso_week} ({start_date} to {end_date})")

        for market in top_8_markets:
            # ✅ Filter data for the current market & week
            market_df = data[(data["Country"] == market) & (data["Date"] >= start_date) & (data["Date"] <= end_date)]

            if market_df.empty:
                sessions = 0
                print(f"  ⚠️ No data found for {market} in week {iso_week}")
            else:
                # ✅ Calculate sessions as a proxy based on market size
                # Use unique customers as a proxy for sessions
                unique_customers = market_df['Customer E-mail'].nunique()
                unique_orders = market_df['Order No'].nunique()

                # Estimate sessions based on customers and orders
                # Typical e-commerce: 3-5 sessions per customer, 1-2 sessions per order
                estimated_sessions = max(unique_customers * 4, unique_orders * 1.5)
                sessions = int(estimated_sessions)

                print(f"  📊 {market}: {sessions:,} sessions (est. from {unique_customers:,} customers, {unique_orders:,} orders)")

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
