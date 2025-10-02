import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.metrics_calculator import load_data
from calculator.date_utils import get_last_8_weeks, get_last_8_weeks_last_year

data = load_data()

def load_sessions_data():
    """Load the session_data.csv with country breakdown."""
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

def load_orders_data():
    """Load and deduplicate orders data from weekly_data_formatted.csv"""
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    orders_file = os.path.join(BASE_DIR, "data", "formatted", "weekly_data_formatted.csv")
    
    orders_df = pd.read_csv(orders_file, sep=",", decimal=".")
    orders_df['Date'] = pd.to_datetime(orders_df['Date'])
    
    print(f"\n📊 **Loaded Orders Data:**")
    print(f"  - Total rows: {len(orders_df)}")
    print(f"  - Date range: {orders_df['Date'].min()} to {orders_df['Date'].max()}")
    print(f"  - Unique countries: {orders_df['Country'].nunique()}")
    print(f"  - Sample countries: {list(orders_df['Country'].unique()[:10])}")
    
    return orders_df

sessions_data = load_sessions_data()
orders_data = load_orders_data()

def get_conversion_markets():
    """
    Returns the specific markets for conversion rate data as requested.
    Markets: Total, USA, Sweden, United Kingdom, Germany, Australia, Canada, France, ROW
    """
    return [
        "Total",
        "United States",
        "Sweden", 
        "United Kingdom",
        "Germany",
        "Australia",
        "Canada",
        "France",
        "ROW",
    ]

def country_match_mapping():
    """
    Maps session country names to order country names where they differ
    """
    mapping = {
        "United States": "USA",
        "United Kingdom": "UK", 
        # Add other mappings as needed
    }
    return mapping

def get_unique_orders_for_week(df, start_date, end_date, country=None):
    """
    Get unique order count for a specific week and country.
    Deduplicates orders like in existing metrics_calculator.
    """
    # Convert dates to datetime for consistent comparison
    start_date_dt = pd.to_datetime(start_date)
    end_date_dt = pd.to_datetime(end_date)
    
    # Filter data for the selected week & online channel
    filtered_df = df[
        (df["Date"] >= start_date_dt) &
        (df["Date"] <= end_date_dt) &
        (df["Sales Channel"] == "Online") &
        (df["Order No"] != "-")  # Exclude invalid Order IDs
    ]
    
    # Apply country filter if specified
    if country:
        filtered_df = filtered_df[filtered_df["Country"] == country]
    
    # Deduplication: Keep first occurrence for each Order No
    unique_orders = filtered_df.drop_duplicates(subset=["Order No"], keep="first")
    
    return len(unique_orders)

def get_sessions_for_week(df, start_date, end_date, country=None):
    """
    Get total sessions for a specific week and country.
    """
    # Filter by date range
    week_sessions_data = df[
        (df["Day"] >= pd.to_datetime(start_date)) & 
        (df["Day"] <= pd.to_datetime(end_date)) &
        (df["Session country"].notna())
    ]
    
    # Apply country filter if specified
    if country:
        week_sessions_data = week_sessions_data[week_sessions_data["Session country"] == country]
    
    # Return total sessions
    return int(week_sessions_data["Sessions"].sum())

def calculate_conversion_market_data(weekly_ranges, year_label):
    """Calculates weekly conversion rate data for specified markets for a given set of week ranges."""

    weekly_conversions = []
    markets = get_conversion_markets()
    country_mapping = country_match_mapping()

    print(f"\n📊 **Conversion Markets (Order as specified):**")
    for i, market in enumerate(markets, 1):
        print(f"  {i}. {market}")

    for week in weekly_ranges:
        start_date, end_date = week["week_start"], week["week_end"]
        iso_week = week["week_start"].isocalendar()[1]
        calendar_year = week["week_start"].year

        print(f"\n📆 Processing {year_label}: Week {iso_week} ({start_date} to {end_date})")

        # Get total sessions and orders for Total calculation
        total_sessions = get_sessions_for_week(sessions_data, start_date, end_date)
        total_orders = get_unique_orders_for_week(orders_data, start_date, end_date)
        total_conversion = (total_orders / total_sessions * 100) if total_sessions > 0 else 0

        print(f"  📊 Total: {total_orders:,} orders / {total_sessions:,} sessions = {total_conversion:.2f}%")

        for market in markets:
            if market == "Total":
                conversion_rate = total_conversion
                print(f"  📊 {market}: {conversion_rate:.2f}% (total)")
            elif market == "ROW":
                # Calculate ROW sessions and orders
                specific_markets = ["United States", "Sweden", "United Kingdom", "Germany", "Australia", "Canada", "France"]
                
                # Get sessions for ROW countries (all sessions - specific markets)
                row_sessions_filter = sessions_data[
                    (sessions_data["Day"] >= pd.to_datetime(start_date)) & 
                    (sessions_data["Day"] <= pd.to_datetime(end_date)) & 
                    (sessions_data["Session country"].notna()) &
                    (~sessions_data["Session country"].isin(specific_markets))
                ]
                row_sessions = int(row_sessions_filter["Sessions"].sum())
                
                # Get orders for ROW countries (countries not in specific markets)
                order_countries_to_exclude = ["USA", "Sweden", "United Kingdom", "Germany", "Australia", "Canada", "France"]
                row_orders_filter = orders_data[
                    (orders_data["Date"] >= pd.to_datetime(start_date)) &
                    (orders_data["Date"] <= pd.to_datetime(end_date)) &
                    (orders_data["Sales Channel"] == "Online") &
                    (orders_data["Order No"] != "-") &
                    (~orders_data["Country"].isin(order_countries_to_exclude))
                ]
                row_orders = len(row_orders_filter.drop_duplicates(subset=["Order No"], keep="first"))
                
                conversion_rate = (row_orders / row_sessions * 100) if row_sessions > 0 else 0
                print(f"  📊 {market}: {row_orders:,} orders / {row_sessions:,} sessions = {conversion_rate:.2f}%")
                
            else:
                # Get country mapping for order data
                session_country = market
                order_country = country_mapping.get(market, market)
                
                # Get sessions for specific country
                country_sessions = get_sessions_for_week(sessions_data, start_date, end_date, session_country)
                
                # Get orders for specific country
                country_orders = get_unique_orders_for_week(orders_data, start_date, end_date, order_country)
                
                conversion_rate = (country_orders / country_sessions * 100) if country_sessions > 0 else 0
                print(f"  📊 {market}: {country_orders:,} orders / {country_sessions:,} sessions = {conversion_rate:.2f}%")

            # Append data with "Year Type", "Calendar Year", "ISO Week", "Market", and "Conversion Rate"
            weekly_conversions.append({
                "Year Type": year_label,
                "Calendar Year": calendar_year,
                "ISO Week": iso_week,
                "Market": market,
                "Value": conversion_rate
            })
    
    return pd.DataFrame(weekly_conversions)

# Get week ranges
last_8_weeks, _ = get_last_8_weeks()
last_8_weeks_last_year, _ = get_last_8_weeks_last_year()

last_8_weeks_order = [
    (week["week_start"].year, week["week_start"].isocalendar()[1]) for week in last_8_weeks
]
last_8_weeks_last_year_order = [
    (week["week_start"].year, week["week_start"].isocalendar()[1]) for week in last_8_weeks_last_year
]

print("\n📆 **Expected Current Year Order:**", last_8_weeks_order)
print("\n📆 **Expected Last Year Order:**", last_8_weeks_last_year_order)

# Calculate conversion rates for both years
conversions_current_year = calculate_conversion_market_data(last_8_weeks, "Current Year")
conversions_last_year = calculate_conversion_market_data(last_8_weeks_last_year, "Last Year")

# Combine data
conversions_final = pd.concat([conversions_last_year, conversions_current_year])

# Sort data correctly
conversions_final["SortOrder"] = conversions_final.apply(
    lambda row: last_8_weeks_order.index((row["Calendar Year"], row["ISO Week"]))
    if (row["Calendar Year"], row["ISO Week"]) in last_8_weeks_order else float("inf"),
    axis=1
)

conversions_final = conversions_final.sort_values(by="SortOrder").drop(columns=["SortOrder"])

print("\n📊 **Final Conversion Markets DataFrame (First Rows)**")
print(conversions_final[["Year Type", "Calendar Year", "ISO Week", "Market"]].drop_duplicates())

# Save to CSV
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

output_path = os.path.join(OUTPUT_DIR, "conversion_markets_raw.csv")
conversions_final.to_csv(output_path, index=False, sep=";", decimal=",")

print(f"\n✅ **Conversion Markets data saved to:** {output_path}")
print(f"📊 **Total rows:** {len(conversions_final)}")
print(f"📊 **Markets:** {conversions_final['Market'].nunique()}")
print(f"📊 **Weeks:** {conversions_final['ISO Week'].nunique()}")
print(f"📊 **Years:** {conversions_final['Year Type'].nunique()}")
