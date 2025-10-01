import sys
import os
import pandas as pd

# Add the scripts folder to Python's import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import necessary functions
from calculator.metrics_calculator import (
    load_data,
    load_spend_data,
    calculate_revenue_metrics,
    calculate_marketing_spend
)

from calculator.date_utils import get_latest_full_week

# Define output file path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))  
RAW_METRICS_OUTPUT_PATH = os.path.join(BASE_DIR, "data", "raw", "metrics_raw.csv")

# Define all required metrics
METRIC_NAMES = [
    "Online Gross Revenue before Discount",
    "Discounts",
    "Discount rate %",
    "Online Gross Revenue",
    "Returns",
    "Return rate %",
    "Online Net Revenue",
    "Retail Concept Store",
    "Retail Pop-ups, Outlets",
    "Retail Archive Sale, Stockholm",
    "Retail Archive Sale, Göteborg",
    "Retail Outlet, Barkarby",
    "Retail Pop-up, Mykonos",
    "Retail Pop-up, Miami",
    "Retail Net Revenue",
    "Wholesale Net Revenue",
    "Total Net Revenue",
    "Returning Customers",
    "New Customers",
    "Marketing Spend",
    "Online Cost of Sale (CoS)",
    "Online nCAC (SEK)(4)"
]

def load_and_prepare_data():
    """Computes all revenue & cost metrics for Current Week, Last Week, Last Year, and 2023."""
    df = load_data()
    spend_df = load_spend_data()
    time_periods = get_latest_full_week()

    # ✅ Extract the **current week dates**
    current_week_start, current_week_end = time_periods["current_week"]
    print(f"\n📆 **Current Week: {current_week_start} → {current_week_end}**")

    # Initialize metrics dictionary with "-" values for missing data
    metrics = {metric: {period: "-" for period in time_periods.keys()} for metric in METRIC_NAMES}

    # Calculate revenue & marketing spend for each time period
    for period_name, (start, end) in time_periods.items():
        revenue_data = calculate_revenue_metrics(df, start, end)
        new_customers = revenue_data.get("New Customers", 0)  # Ensure new_customers is retrieved
        spend, cost_of_sale, ncac = calculate_marketing_spend(spend_df, start, end, revenue_data.get("Gross Revenue", 0), new_customers)

        # Fill in available data, replace missing values with "-"
        metrics["Online Gross Revenue before Discount"][period_name] = revenue_data.get("Gross Revenue Before Discount", "-")
        metrics["Discounts"][period_name] = revenue_data.get("Discounts", "-")
        metrics["Discount rate %"][period_name] = revenue_data.get("Discount Rate", "-")
        metrics["Online Gross Revenue"][period_name] = revenue_data.get("Gross Revenue", "-")
        metrics["Returns"][period_name] = revenue_data.get("Returns", "-")
        metrics["Return rate %"][period_name] = revenue_data.get("Return Rate", "-")
        metrics["Online Net Revenue"][period_name] = revenue_data.get("Net Revenue", "-")
        
        # ✅ Retail & Wholesale Revenues (Ensure we pull the correct values)
        metrics["Retail Concept Store"][period_name] = revenue_data.get("Retail Concept Store Revenue", "-")
        metrics["Retail Pop-ups, Outlets"][period_name] = revenue_data.get("Retail Pop-ups Revenue", "-")
        metrics["Retail Archive Sale, Stockholm"][period_name] = revenue_data.get("Retail Archive Sale, Stockholm", "-")
        metrics["Retail Archive Sale, Göteborg"][period_name] = revenue_data.get("Retail Archive Sale, Göteborg", "-")
        metrics["Retail Outlet, Barkarby"][period_name] = revenue_data.get("Retail Outlet, Barkarby", "-")
        metrics["Retail Pop-up, Mykonos"][period_name] = revenue_data.get("Retail Pop-up, Mykonos", "-")
        metrics["Retail Pop-up, Miami"][period_name] = revenue_data.get("Retail Pop-up, Miami", "-")
        metrics["Retail Net Revenue"][period_name] = revenue_data.get("Retail Net Revenue", "-")
        metrics["Wholesale Net Revenue"][period_name] = revenue_data.get("Wholesale Net Revenue", "-")

        # ✅ Ensure Total Net Revenue includes Online, Retail, and Wholesale
        total_net_revenue = (
            revenue_data.get("Net Revenue", 0) + 
            revenue_data.get("Retail Net Revenue", 0) + 
            revenue_data.get("Wholesale Net Revenue", 0)
        )
        metrics["Total Net Revenue"][period_name] = total_net_revenue if total_net_revenue else "-"

        # ✅ Customer Metrics
        metrics["Returning Customers"][period_name] = revenue_data.get("Returning Customers", "-")
        metrics["New Customers"][period_name] = revenue_data.get("New Customers", "-")

        # ✅ Marketing Spend & Performance
        metrics["Marketing Spend"][period_name] = spend if spend is not None else "-"
        metrics["Online Cost of Sale (CoS)"][period_name] = cost_of_sale if cost_of_sale is not None else "-"
        metrics["Online nCAC (SEK)(4)"][period_name] = ncac if ncac is not None else "-"

    # Convert to DataFrame
    metrics_df = pd.DataFrame.from_dict(metrics, orient="index")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(RAW_METRICS_OUTPUT_PATH), exist_ok=True)

    # Save raw metrics (unformatted)
    metrics_df.to_csv(RAW_METRICS_OUTPUT_PATH, index=True)
    print(f"✅ Raw Metrics saved to `{RAW_METRICS_OUTPUT_PATH}`")

    print(metrics_df)  # Debug output to verify

if __name__ == "__main__":
    load_and_prepare_data()
