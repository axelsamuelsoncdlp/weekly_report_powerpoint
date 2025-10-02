import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.metrics_calculator import load_data
from calculator.date_utils import get_last_8_weeks, get_last_8_weeks_last_year

data = load_data()

def get_aov_new_markets():
    """
    Returns the specific markets for AOV new customers data as requested.
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

def get_aov_new_customers_for_week(df, start_date, end_date, country=None):
    """
    Calculate Average Order Value (AOV) for new customers in a specific week and country.
    AOV = Total Revenue from new customers / Number of orders from new customers
    """
    # Convert dates to date for consistent comparison (load_data uses .dt.date)
    start_date_dt = start_date
    end_date_dt = end_date
    
    # Filter data for the selected week & online channel & new customers
    filtered_df = df[
        (df["Date"] >= start_date_dt) &
        (df["Date"] <= end_date_dt) &
        (df["Sales Channel"] == "Online") &
        (df["New/Returning Customer"] == "New") &
        (df["Order No"] != "-") &  # Exclude invalid order numbers
        (df["Country"] != "-")     # Exclude invalid countries
    ]
    
    # Apply country filter if specified
    if country:
        filtered_df = filtered_df[filtered_df["Country"] == country]
    
    # Filter out zero-value orders (free orders or returns)
    filtered_df = filtered_df[filtered_df["Gross Revenue"] > 0]
    
    if len(filtered_df) == 0:
        return 0  # No orders = 0 AOV
    
    # Calculate AOV: Total Revenue / Number of unique orders
    total_revenue = filtered_df["Gross Revenue"].sum()
    
    # Deduplicate orders (same order number could appear multiple times for different products)
    unique_orders = filtered_df["Order No"].nunique()
    
    aov = total_revenue / unique_orders if unique_orders > 0 else 0
    
    return aov

def calculate_aov_new_markets_data(weekly_ranges, year_label):
    """Calculates weekly AOV for new customers in specified markets for a given set of week ranges."""

    weekly_aov_new = []
    markets = get_aov_new_markets()
    country_mapping = country_match_mapping()

    print(f"\n📊 **AOV New Customers Markets (Order as specified):**")
    for i, market in enumerate(markets, 1):
        print(f"  {i}. {market}")

    for week in weekly_ranges:
        start_date, end_date = week["week_start"], week["week_end"]
        iso_week = week["week_start"].isocalendar()[1]
        calendar_year = week["week_start"].year

        print(f"\n📆 Processing {year_label}: Week {iso_week} ({start_date} to {end_date})")

        # Get total AOV for new customers for Total calculation
        total_aov = get_aov_new_customers_for_week(data, start_date, end_date)
        print(f"  📊 Total: AOV ${total_aov:.2f} for new customers")

        for market in markets:
            if market == "Total":
                aov_value = total_aov
                print(f"  📊 {market}: AOV ${aov_value:.2f} (total)")
            elif market == "ROW":
                # Calculate AOV for ROW countries (countries not in specific markets)
                specific_markets = ["United States", "Sweden", "United Kingdom", "Germany", "Australia", "Canada", "France"]
                
                # Start with all new customers data in the week
                start_date_dt = start_date  
                end_date_dt = end_date
                
                all_new_customers_data = data[
                    (data["Date"] >= start_date_dt) &
                    (data["Date"] <= end_date_dt) &
                    (data["Sales Channel"] == "Online") &
                    (data["New/Returning Customer"] == "New") &
                    (data["Order No"] != "-") &
                    (data["Country"] != "-")
                ]
                
                # Filter for ROW countries and exclude zero-value orders
                row_customers_data = all_new_customers_data[
                    (~all_new_customers_data["Country"].isin(specific_markets)) &
                    (all_new_customers_data["Country"].notna()) &
                    (all_new_customers_data["Gross Revenue"] > 0)
                ]
                
                if len(row_customers_data) == 0:
                    aov_value = 0
                else:
                    total_revenue = row_customers_data["Gross Revenue"].sum()
                    unique_orders = row_customers_data["Order No"].nunique()
                    aov_value = total_revenue / unique_orders if unique_orders > 0 else 0
                
                print(f"  📊 {market}: AOV ${aov_value:.2f} (ROW)")
            else:
                # Get country mapping for specific market
                order_country = country_mapping.get(market, market)
                
                # Get AOV for specific country
                aov_value = get_aov_new_customers_for_week(data, start_date, end_date, order_country)
                print(f"  📊 {market}: AOV ${aov_value:.2f}")

            # Append data with "Year Type", "Calendar Year", "ISO Week", "Market", and "AOV"
            weekly_aov_new.append({
                "Year Type": year_label,
                "Calendar Year": calendar_year,
                "ISO Week": iso_week,
                "Market": market,
                "Value": aov_value
            })
    
    return pd.DataFrame(weekly_aov_new)

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

# Calculate AOV for new customers for both years
aov_new_current_year = calculate_aov_new_markets_data(last_8_weeks, "Current Year")
aov_new_last_year = calculate_aov_new_markets_data(last_8_weeks_last_year, "Last Year")

# Combine data
aov_new_final = pd.concat([aov_new_last_year, aov_new_current_year])

# Sort data correctly
aov_new_final["SortOrder"] = aov_new_final.apply(
    lambda row: last_8_weeks_order.index((row["Calendar Year"], row["ISO Week"]))
    if (row["Calendar Year"], row["ISO Week"]) in last_8_weeks_order else float("inf"),
    axis=1
)

aov_new_final = aov_new_final.sort_values(by="SortOrder").drop(columns=["SortOrder"])

print("\n📊 **Final AOV New Customers Markets DataFrame (First Rows)**")
print(aov_new_final[["Year Type", "Calendar Year", "ISO Week", "Market"]].drop_duplicates())

# Save to CSV
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

output_path = os.path.join(OUTPUT_DIR, "aov_new_markets_raw.csv")
aov_new_final.to_csv(output_path, index=False, sep=";", decimal=",")

print(f"\n✅ **AOV New Customers Markets data saved to:** {output_path}")
print(f"📊 **Total rows:** {len(aov_new_final)}")
print(f"📊 **Markets:** {aov_new_final['Market'].nunique()}")
print(f"📊 **Weeks:** {aov_new_final['ISO Week'].nunique()}")
print(f"📊 **Years:** {aov_new_final['Year Type'].nunique()}")
