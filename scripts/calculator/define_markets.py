import sys
import os
import pandas as pd
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Add scripts folder to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.metrics_calculator import load_data, calculate_revenue_metrics
from calculator.date_utils import get_last_8_weeks

def get_latest_week(weeks_list):
    """
    Ensures the latest available week is correctly identified by sorting by year and ISO week.
    """
    sorted_weeks = sorted(weeks_list, key=lambda x: (x["week_start"].year, x["week_start"].isocalendar()[1]), reverse=True)
    latest_week = sorted_weeks[0]  # Most recent week
    return latest_week["week_start"], latest_week["week_end"]

def get_top_markets(df):
    """
    Dynamically determines the top 15 markets based on Online Gross Revenue
    from the most recent **correctly selected** week.
    """
    weeks_list, _ = get_last_8_weeks()
    start, end = get_latest_week(weeks_list)

    # ✅ Aggregate revenue by market for the latest week
    market_revenue = {}
    for market in df["Country"].unique():
        market_df = df[(df["Country"] == market) & (df["Date"] >= start) & (df["Date"] <= end)]
        if not market_df.empty:
            revenue_data = calculate_revenue_metrics(market_df, start, end)
            market_revenue[market] = revenue_data.get("Gross Revenue", 0)

    # ✅ Sort markets by revenue and get the top 15
    sorted_markets = sorted(market_revenue.items(), key=lambda x: x[1], reverse=True)
    top_markets = [market for market, _ in sorted_markets[:15]]

    return top_markets, market_revenue

def get_row(df, top_markets, market_revenue):
    """
    Calculates revenue for ROW (Rest of World) by summing revenue
    of all remaining markets that are **not** in the top 15.
    """
    row_markets = [market for market in df["Country"].unique() if market not in top_markets]
    row_revenue = sum(market_revenue.get(market, 0) for market in row_markets)

    return "ROW", row_revenue

def get_all_markets():
    """
    Returns the dynamically selected top 15 markets plus ROW (Rest of World) and Total.
    """
    df = load_data()
    top_markets, market_revenue = get_top_markets(df)
    row_market, row_revenue = get_row(df, top_markets, market_revenue)

    # ✅ Calculate TOTAL Revenue (Top 15 + ROW)
    total_revenue = sum(market_revenue.get(market, 0) for market in top_markets) + row_revenue

    return top_markets + [row_market, "Total"]

if __name__ == "__main__":
    # ✅ Ensure script runs and prints markets when executed
    markets = get_all_markets()
