import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.metrics_calculator import load_data
from calculator.date_utils import get_last_8_weeks, get_last_8_weeks_last_year

data = load_data()

def get_new_customers_markets():
    """
    Returns the specific markets for new customers data as requested.
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
    Maps market names to country names where they differ
    """
    mapping = {
        "United States": "United States",
        "United Kingdom": "United Kingdom",
        # Add other mappings as needed
    }
    return mapping

def get_new_customers_for_week(df, start_date, end_date, country=None):
    """
    Get unique new customers count for a specific week and country.
    Deduplicates customers like in existing metrics_calculator.
    """
    # Convert dates to date for consistent comparison (load_data uses .dt.date)
    start_date_dt = start_date
    end_date_dt = end_date
    
    # Filter data for the selected week & online channel
    filtered_df = df[
        (df["Date"] >= start_date_dt) &
        (df["Date"] <= end_date_dt) &
        (df["Sales Channel"] == "Online") &
        (df["New/Returning Customer"] == "New") &
        (df["Customer E-mail"] != "-")  # Exclude invalid customer emails
    ]
    
    # Apply country filter if specified
    if country:
        filtered_df = filtered_df[filtered_df["Country"] == country]
    
    # Deduplication: Keep first occurrence for each Customer E-mail
    unique_new_customers = filtered_df.drop_duplicates(subset=["Customer E-mail"], keep="first")
    
    return len(unique_new_customers)

def calculate_new_customers_market_data(weekly_ranges, year_label):
    """Calculates weekly new customers data for specified markets for a given set of week ranges."""

    weekly_new_customers = []
    markets = get_new_customers_markets()
    country_mapping = country_match_mapping()

    print(f"\n📊 **New Customers Markets (Order as specified):**")
    for i, market in enumerate(markets, 1):
        print(f"  {i}. {market}")

    for week in weekly_ranges:
        start_date, end_date = week["week_start"], week["week_end"]
        iso_week = week["week_start"].isocalendar()[1]
        calendar_year = week["week_start"].year

        print(f"\n📆 Processing {year_label}: Week {iso_week} ({start_date} to {end_date})")

        # Get total new customers for Total calculation
        total_new_customers = get_new_customers_for_week(data, start_date, end_date)
        print(f"  📊 Total: {total_new_customers:,} new customers")

        for market in markets:
            if market == "Total":
                new_customers_count = total_new_customers
                print(f"  📊 {market}: {new_customers_count:,} new customers (total)")
            elif market == "ROW":
                # Calculate ROW new customers (customers not in specific markets)
                specific_markets = ["United States", "Sweden", "United Kingdom", "Germany", "Australia", "Canada", "France"]
                
                # Start with all new customers in the week
                start_date_dt = start_date  
                end_date_dt = end_date
                
                all_new_customers = data[
                    (data["Date"] >= start_date_dt) &
                    (data["Date"] <= end_date_dt) &
                    (data["Sales Channel"] == "Online") &
                    (data["New/Returning Customer"] == "New") &
                    (data["Customer E-mail"] != "-")
                ]
                
                # Get customers from other countries (ROW)
                row_customers = all_new_customers[
                    (~all_new_customers["Country"].isin(specific_markets)) &
                    (all_new_customers["Country"] != "-") &
                    (all_new_customers["Country"].notna())
                ]
                
                # Deduplicate ROW customers
                unique_row_customers = row_customers.drop_duplicates(subset=["Customer E-mail"], keep="first")
                new_customers_count = len(unique_row_customers)
                
                print(f"  📊 {market}: {new_customers_count:,} new customers (ROW)")
            else:
                # Get country mapping for specific market
                order_country = country_mapping.get(market, market)
                
                # Get new customers for specific country
                new_customers_count = get_new_customers_for_week(data, start_date, end_date, order_country)
                print(f"  📊 {market}: {new_customers_count:,} new customers")

            # Append data with "Year Type", "Calendar Year", "ISO Week", "Market", and "New Customers"
            weekly_new_customers.append({
                "Year Type": year_label,
                "Calendar Year": calendar_year,
                "ISO Week": iso_week,
                "Market": market,
                "Value": new_customers_count
            })
    
    return pd.DataFrame(weekly_new_customers)

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

# Calculate new customers for both years
new_customers_current_year = calculate_new_customers_market_data(last_8_weeks, "Current Year")
new_customers_last_year = calculate_new_customers_market_data(last_8_weeks_last_year, "Last Year")

# Combine data
new_customers_final = pd.concat([new_customers_last_year, new_customers_current_year])

# Sort data correctly
new_customers_final["SortOrder"] = new_customers_final.apply(
    lambda row: last_8_weeks_order.index((row["Calendar Year"], row["ISO Week"]))
    if (row["Calendar Year"], row["ISO Week"]) in last_8_weeks_order else float("inf"),
    axis=1
)

new_customers_final = new_customers_final.sort_values(by="SortOrder").drop(columns=["SortOrder"])

print("\n📊 **Final New Customers Markets DataFrame (First Rows)**")
print(new_customers_final[["Year Type", "Calendar Year", "ISO Week", "Market"]].drop_duplicates())

# Save to CSV
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

output_path = os.path.join(OUTPUT_DIR, "new_customers_markets_raw.csv")
new_customers_final.to_csv(output_path, index=False, sep=";", decimal=",")

print(f"\n✅ **New Customers Markets data saved to:** {output_path}")
print(f"📊 **Total rows:** {len(new_customers_final)}")
print(f"📊 **Markets:** {new_customers_final['Market'].nunique()}")
print(f"📊 **Weeks:** {new_customers_final['ISO Week'].nunique()}")
print(f"📊 **Years:** {new_customers_final['Year Type'].nunique()}")
