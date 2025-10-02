import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.date_utils import get_last_8_weeks, get_last_8_weeks_last_year

def load_spend_data():
    """Load marketing spend data"""
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    spend_file = os.path.join(BASE_DIR, "data", "formatted", "marketing_spend_final.csv")
    
    print(f"📊 **Loading spend data from:** {spend_file}")
    
    if not os.path.exists(spend_file):
        raise FileNotFoundError(f"❌ Spend data file not found: {spend_file}")
    
    df = pd.read_csv(spend_file)
    df["Date"] = pd.to_datetime(df["Date"])
    
    print(f"📊 **Spend data loaded:** {len(df)} rows")
    print(f"🧹 **Cleaning data...**")
    
    # Clean data - remove NaN markets and convert spend to numeric
    df = df.dropna(subset=["Market"])
    df["Total Spend"] = pd.to_numeric(df["Total Spend"], errors="coerce")
    df = df.dropna(subset=["Total Spend"])
    
    print(f"📊 **After cleaning:** {len(df)} rows")
    print(f"📊 **Date range:** {df['Date'].min()} to {df['Date'].max()}")
    print(f"📊 **Markets:** {df['Market'].nunique()}")
    
    return df

def get_online_media_spend_markets():
    """
    Returns the specific markets for online media spend data.
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

def market_code_mapping():
    """
    Maps market names to country codes used in spend data
    """
    return {
        "United States": "US",
        "Sweden": "SE",
        "United Kingdom": "GB",
        "Germany": "DE",
        "Australia": "AU",
        "Canada": "CA",
        "France": "FR",
    }

def get_spend_for_week(df, start_date, end_date, country_code=None):
    """
    Get total spend for a specific week and country.
    """
    # Convert dates to consistent datetime
    start_date_dt = pd.to_datetime(start_date)
    end_date_dt = pd.to_datetime(end_date)
    
    # Filter data for the selected week
    week_df = df[
        (df["Date"] >= start_date_dt) &
        (df["Date"] <= end_date_dt)
    ]
    
    # Apply country filter if specified
    if country_code:
        week_df = week_df[week_df["Market"] == country_code]
    
    # Sum total spend for the week
    total_spend = week_df["Total Spend"].sum() if len(week_df) > 0 else 0
    
    return total_spend

def calculate_online_media_spend_data(weekly_ranges, year_label, spend_data):
    """Calculates weekly spend data for specified markets for a given set of week ranges."""

    weekly_spend = []
    markets = get_online_media_spend_markets()
    market_mapping = market_code_mapping()

    print(f"\n📊 **Online Media Spend Markets (Order as specified):**")
    for i, market in enumerate(markets, 1):
        print(f"  {i}. {market}")

    for week in weekly_ranges:
        start_date, end_date = week["week_start"], week["week_end"]
        iso_week = week["week_start"].isocalendar()[1]
        calendar_year = week["week_start"].year

        print(f"\n📆 Processing {year_label}: Week {iso_week} ({start_date} to {end_date})")

        # Get total spend for Total calculation
        total_spend = get_spend_for_week(spend_data, start_date, end_date)
        print(f"  📊 Total: Spend ${total_spend:.2f}")

        for market in markets:
            spend_value = 0
            
            if market == "Total":
                spend_value = total_spend
                print(f"  📊 {market}: Spend ${spend_value:.2f} (total)")
            elif market == "ROW":
                # Calculate spend for ROW countries (not in specific markets)
                specific_markets_codes = ["US", "SE", "GB", "DE", "AU", "CA", "FR"]
                
                # Start with all spend data in the week
                week_df = spend_data[
                    (pd.to_datetime(spend_data["Date"]) >= pd.to_datetime(start_date)) &
                    (pd.to_datetime(spend_data["Date"]) <= pd.to_datetime(end_date))
                ]
                
                # Filter for ROW countries (excluding specific markets)
                row_spend_df = week_df[
                    ~week_df["Market"].isin(specific_markets_codes)
                ]
                
                spend_value = row_spend_df["Total Spend"].sum() if len(row_spend_df) > 0 else 0
                
                print(f"  📊 {market}: Spend ${spend_value:.2f} (ROW)")
            else:
                # Get country mapping for specific market
                country_code = market_mapping.get(market)
                
                if country_code:
                    # Get spend for specific country
                    spend_value = get_spend_for_week(spend_data, start_date, end_date, country_code)
                    print(f"  📊 {market}: Spend ${spend_value:.2f} ({country_code})")
                else:
                    print(f"  ❌ {market}: No country code mapping found")

            # Append data with "Year Type", "Calendar Year", "ISO Week", "Market", and "Value"
            weekly_spend.append({
                "Year Type": year_label,
                "Calendar Year": calendar_year,
                "ISO Week": iso_week,
                "Market": market,
                "Value": spend_value
            })
    
    return pd.DataFrame(weekly_spend)

# Load spend data
spend_data = load_spend_data()

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

# Calculate spend for both years
online_media_spend_current_year = calculate_online_media_spend_data(last_8_weeks, "Current Year", spend_data)
online_media_spend_last_year = calculate_online_media_spend_data(last_8_weeks_last_year, "Last Year", spend_data)

# Combine data
online_media_spend_final = pd.concat([online_media_spend_last_year, online_media_spend_current_year])

# Sort data correctly
online_media_spend_final["SortOrder"] = online_media_spend_final.apply(
    lambda row: last_8_weeks_order.index((row["Calendar Year"], row["ISO Week"]))
    if (row["Calendar Year"], row["ISO Week"]) in last_8_weeks_order else float("inf"),
    axis=1
)

online_media_spend_final = online_media_spend_final.sort_values(by="SortOrder").drop(columns=["SortOrder"])

print("\n📊 **Final Online Media Spend Markets DataFrame (First Rows)**")
print(online_media_spend_final[["Year Type", "Calendar Year", "ISO Week", "Market"]].drop_duplicates())

# Save to CSV
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

output_path = os.path.join(OUTPUT_DIR, "online_media_spend_raw.csv")
online_media_spend_final.to_csv(output_path, index=False, sep=";", decimal=",")

print(f"\n✅ **Online Media Spend Markets data saved to:** {output_path}")
print(f"📊 **Total rows:** {len(online_media_spend_final)}")
print(f"📊 **Markets:** {online_media_spend_final['Market'].nunique()}")
print(f"📊 **Weeks:** {online_media_spend_final['ISO Week'].nunique()}")
print(f"📊 **Years:** {online_media_spend_final['Year Type'].nunique()}")
