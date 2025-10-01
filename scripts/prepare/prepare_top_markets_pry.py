import sys
import os
import pandas as pd
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Add script directory to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import functions
from calculator.metrics_calculator import load_data, load_spend_data, calculate_revenue_metrics, calculate_marketing_spend
from calculator.date_utils import get_last_8_weeks_last_year
from calculator.define_markets import get_all_markets

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
TOP_MARKETS_OUTPUT_PATH = os.path.join(BASE_DIR, "data", "raw", "top_markets_pry_raw.csv")

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
    """Generate week labels for the last year."""
    return [f"Vecka {week['week_start'].isocalendar()[1]} ({week['week_start'].year})" for week in reversed(weeks_list)]

def load_and_prepare_top_markets_pry():
    """Computes revenue and marketing metrics for top markets."""
    logging.info("📌 Loading data sources...")
    df, spend_df = load_data(), load_spend_data()
    weeks_list, _ = get_last_8_weeks_last_year()
    all_markets = get_all_markets()
    week_labels = get_week_labels(weeks_list)

    # ✅ Log all extracted weeks with their start & end dates
    logging.info("\n📆 **Extracted Last 8 ISO Weeks with Dates:**")
    for week in weeks_list:
        start, end = week["week_start"], week["week_end"]
        logging.info(f"🗓️ Vecka {start.isocalendar()[1]} ({start.year}): {start} → {end}")  

    # ✅ Log all selected markets
    logging.info("\n🌍 **Selected Markets (Including ROW & Total if applicable):**")
    logging.info(", ".join(all_markets))

    metrics_dict = {(market, metric): {} for market in all_markets for metric in METRIC_MAPPING.values()}

    for week in reversed(weeks_list):
        start, end = week["week_start"], week["week_end"]
        week_label = f"Vecka {start.isocalendar()[1]} ({start.year})"

        for market in all_markets:
            if market == "ROW":
                market_df = df[~df["Country"].isin(all_markets[:-2]) & (df["Date"] >= start) & (df["Date"] <= end)]
            elif market == "Total":
                market_df = df[(df["Date"] >= start) & (df["Date"] <= end)]
            else:
                market_df = df[(df["Country"] == market) & (df["Date"] >= start) & (df["Date"] <= end)]
            
            logging.info(f"🔎 Checking {market} data for {week_label} - Found {len(market_df)} records")

            if market_df.empty:
                for metric in METRIC_MAPPING.values():
                    metrics_dict[(market, metric)][week_label] = "-"
                logging.warning(f"⚠️ No data found for {market} in {week_label}")
                continue

            revenue_data = calculate_revenue_metrics(market_df, start, end)
            for metric, expected_metric in METRIC_MAPPING.items():
                metrics_dict[(market, expected_metric)][week_label] = revenue_data.get(metric, 0)

    # ✅ Convert to DataFrame
    top_markets_df = pd.DataFrame([{**{"Market": m, "Metric": met}, **vals} for (m, met), vals in metrics_dict.items()])
    top_markets_df = top_markets_df[["Market", "Metric"] + week_labels]

    # ✅ Log missing markets if count is incorrect
    unique_markets = top_markets_df["Market"].unique()
    expected_market_count = len(all_markets)
    if len(unique_markets) != expected_market_count:
        missing_markets = set(all_markets) - set(unique_markets)
        logging.error("❌ Incorrect number of top markets: Expected %d, found %d", expected_market_count, len(unique_markets))
        logging.error("🛑 Missing markets: %s", missing_markets)

    # ✅ Extract Gross Revenue for Top 15 markets + ROW + Total for Week 6
    week_6_label = next((week for week in week_labels if "Vecka 6" in week), None)

    if week_6_label:
        logging.info("\n📊 **Gross Revenue for Week 6 (Last Year):**")
        gross_revenue_df = top_markets_df[
            (top_markets_df["Metric"] == "Online Gross Revenue") &
            (top_markets_df["Market"].isin(all_markets))  # Includes ROW & Total
        ][["Market", week_6_label]]

        # ✅ Verify ROW & Total Calculation
        row_value = gross_revenue_df[gross_revenue_df["Market"] == "ROW"][week_6_label].values[0]
        top_15_sum = gross_revenue_df[gross_revenue_df["Market"].isin(all_markets[:15])][week_6_label].sum()
        gross_revenue_df.loc[gross_revenue_df["Market"] == "Total", week_6_label] = top_15_sum + row_value

        logging.info("🔍 Debug Revenue Breakdown:")
        logging.info("ROW Revenue: %.2f", row_value)
        logging.info("Top 15 Sum: %.2f", top_15_sum)
        logging.info("Expected Total: %.2f", top_15_sum + row_value)

        # ✅ Print DataFrame
        logging.info("\n%s", gross_revenue_df.to_string(index=False))

    # ✅ Save to CSV
    os.makedirs(os.path.dirname(TOP_MARKETS_OUTPUT_PATH), exist_ok=True)
    top_markets_df.to_csv(TOP_MARKETS_OUTPUT_PATH, index=False)
    logging.info("✅ Data saved to `%s`", TOP_MARKETS_OUTPUT_PATH)

    return top_markets_df

if __name__ == "__main__":
    load_and_prepare_top_markets()