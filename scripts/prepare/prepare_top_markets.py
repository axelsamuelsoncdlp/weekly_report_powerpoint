import sys
import os
import pandas as pd
import logging
from tabulate import tabulate

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Add script directory to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import necessary functions
from calculator.metrics_calculator import (
    load_data,
    load_spend_data,
    calculate_revenue_metrics,
    calculate_marketing_spend
)

from calculator.date_utils import get_last_8_weeks
from calculator.define_markets import get_all_markets

# Define output file paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))  
TOP_MARKETS_OUTPUT_PATH = os.path.join(BASE_DIR, "data", "raw", "top_markets_raw.csv")

# Define metric categories to track
METRIC_MAPPING = {
    "Gross Revenue": "Online Gross Revenue",
    "Net Revenue": "Online Net Revenue",
    "Returns": "Returns",
    "Return Rate": "Return Rate %",
    "Retail Concept Store": "Retail Concept Store",
    "Retail Pop-ups": "Retail Pop-ups, Outlets",
    "Retail Net Revenue": "Retail Net Revenue",
    "Wholesale Net Revenue": "Wholesale Net Revenue",
    "Total Net Revenue": "Total Net Revenue",
    "New Customers": "New Customers",
    "Returning Customers": "Returning Customers",
    "Marketing Spend": "Marketing Spend",
    "Online Cost of Sale (CoS)": "Online Cost of Sale (CoS)"
}

def get_week_labels(weeks_list):
    """Generate week labels using ISO year for correct rollover handling."""
    return [f"Vecka {week['week_start'].isocalendar()[1]} ({week['week_start'].isocalendar()[0]})" for week in reversed(weeks_list)]

def load_and_prepare_top_markets():
    """Computes revenue and marketing metrics for dynamically selected top markets over the last 8 ISO weeks."""
    logging.info("📌 Loading data sources...")
    df = load_data()
    spend_df = load_spend_data()
    weeks_list, _ = get_last_8_weeks()
    all_markets = get_all_markets()

    # ✅ Store correct week labels
    week_labels = get_week_labels(weeks_list)

    logging.info("📆 Extracted Last 8 ISO Weeks:")
    for week_label in week_labels:
        logging.info(f"🗓️ {week_label}")

    # ✅ Initialize dictionary for all markets and metrics
    metrics_dict = {}

    for market in all_markets:
        for metric_name in METRIC_MAPPING.values():
            metrics_dict[(market, metric_name)] = {}

        for week in reversed(weeks_list):
            start, end = week["week_start"], week["week_end"]
            iso_week = start.isocalendar()[1]  
            iso_year = start.isocalendar()[0]  # Hämta rätt ISO-år
            week_label = f"Vecka {iso_week} ({iso_year})"

            # ✅ Filter data for the current market & week
            if market == "ROW":
                market_df = df[~df["Country"].isin(all_markets[:-2]) & (df["Date"] >= start) & (df["Date"] <= end)]
            elif market == "Total":
                market_df = df[(df["Date"] >= start) & (df["Date"] <= end)]
            else:
                market_df = df[(df["Country"] == market) & (df["Date"] >= start) & (df["Date"] <= end)]

            if market_df.empty:
                for metric_name in METRIC_MAPPING.values():
                    metrics_dict[(market, metric_name)][week_label] = "-"
                logging.warning(f"⚠️ No data found for {market} in {week_label}")
                continue

            # Compute revenue metrics
            revenue_data = calculate_revenue_metrics(market_df, start, end)

            # Compute marketing spend and CoS
            spend, cost_of_sale, ncac = calculate_marketing_spend(spend_df, start, end, revenue_data.get("Gross Revenue", 0), revenue_data.get("New Customers", 0))
            revenue_data["Marketing Spend"] = spend if spend is not None else 0
            revenue_data["Online Cost of Sale (CoS)"] = round(float(cost_of_sale), 1) if cost_of_sale is not None else 0.0

            # Store results
            for key, expected_metric in METRIC_MAPPING.items():
                metrics_dict[(market, expected_metric)][week_label] = revenue_data.get(key, 0)

    # ✅ Convert dictionary to DataFrame
    result_data = []
    for (market, metric), values in metrics_dict.items():
        row = {"Market": market, "Metric": metric, **values}
        result_data.append(row)

    top_markets_df = pd.DataFrame(result_data)

    # ✅ Ensure correct week order
    logging.info("📌 Available columns in DataFrame: %s", top_markets_df.columns.tolist())
    logging.info("📌 Expected week labels: %s", week_labels)
    
    existing_week_labels = [week for week in week_labels if week in top_markets_df.columns]
    top_markets_df = top_markets_df[["Market", "Metric"] + existing_week_labels]

    # ✅ Log missing markets if count is incorrect
    unique_markets = top_markets_df["Market"].unique()
    if len(unique_markets) != 17:
        missing_markets = set(all_markets) - set(unique_markets)
        logging.error("❌ Incorrect number of top markets: Expected 15, found %d", len(unique_markets))
        logging.error("🛑 Missing markets: %s", missing_markets)

    # ✅ Print Gross Revenue for Week 6 and US
    week_6_label = next((week for week in week_labels if "Vecka 6" in week), None)
    if week_6_label:
        us_gross_revenue = top_markets_df[(top_markets_df["Market"] == "US") & (top_markets_df["Metric"] == "Online Gross Revenue")][week_6_label].values
        logging.info("📊 **Gross Revenue for Week 6 (US):** %s", us_gross_revenue[0] if us_gross_revenue else 'N/A')
    
    # ✅ Save to CSV
    os.makedirs(os.path.dirname(TOP_MARKETS_OUTPUT_PATH), exist_ok=True)
    top_markets_df.to_csv(TOP_MARKETS_OUTPUT_PATH, index=False)
    logging.info("✅ Data saved to `%s`", TOP_MARKETS_OUTPUT_PATH)

    return top_markets_df

if __name__ == "__main__":
    load_and_prepare_top_markets()