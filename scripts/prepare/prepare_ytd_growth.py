import sys
import os
import pandas as pd

# Ensure the scripts folder is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import necessary functions
from calculator.metrics_calculator import calculate_growth

# Define file paths
RAW_YTD_METRICS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw/ytd_metrics_raw.csv"))
YTD_GROWTH_OUTPUT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw/ytd_growth_metrics_raw.csv"))

# Define required metric names
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

def calculate_percentage_growth(current, previous):
    """
    Calculates percentage growth: ((current - previous) / previous) * 100.
    Returns formatted growth as a percentage string.
    """
    if previous == 0 or pd.isna(previous):
        return "n/m"  # Avoid division by zero or missing data

    growth = ((current - previous) / previous) * 100
    return f"{growth:.1f}%" if growth >= 0 else f"({abs(growth):.1f}%)"

def load_and_prepare_ytd_growth():
    """Computes and saves growth metrics for Fiscal YTD."""

    # Load raw YTD metrics data
    metrics_df = pd.read_csv(RAW_YTD_METRICS_PATH, index_col=0)

    # Debugging: Print structure of loaded data
    print("\n🔍 **Debug: YTD Metrics DataFrame Structure**")
    print(metrics_df.head())
    print("🔍 Columns:", metrics_df.columns.tolist())
    print("🔍 Index:", metrics_df.index.tolist())

    # Initialize dictionary for storing growth calculations
    growth_data = {metric: {} for metric in METRIC_NAMES}

    for column in ["ytd_last_year", "ytd_two_years"]:
        for metric in METRIC_NAMES:
            try:
                # Get values safely, defaulting to "n/m" if missing
                current_value = metrics_df.at[metric, "ytd_current_month"] if metric in metrics_df.index else "n/m"
                previous_value = metrics_df.at[metric, column] if metric in metrics_df.index else "n/m"

                # Convert to float for calculations
                if current_value != "n/m" and previous_value != "n/m":
                    current_value = float(str(current_value).replace(",", ""))
                    previous_value = float(str(previous_value).replace(",", ""))
                    growth_data[metric][column] = calculate_percentage_growth(current_value, previous_value)
                else:
                    growth_data[metric][column] = "n/m"
            except Exception as e:
                print(f"⚠️ Error calculating YTD growth for {metric}: {e}")
                growth_data[metric][column] = "n/m"  # Handle errors gracefully

    # Convert to DataFrame
    growth_df = pd.DataFrame.from_dict(growth_data, orient="index")

    # Ensure correct column order and rename columns
    growth_df["budget"] = "n/m"
    growth_df["budget_vs_last_year"] = "n/m"
    growth_df = growth_df[["budget", "ytd_last_year", "ytd_two_years", "budget_vs_last_year"]]

    # Ensure output directory exists before saving
    os.makedirs(os.path.dirname(YTD_GROWTH_OUTPUT_PATH), exist_ok=True)

    # Save growth metrics
    growth_df.to_csv(YTD_GROWTH_OUTPUT_PATH, index=True)

    print(f"\n✅ Fiscal YTD Growth Metrics saved to `{YTD_GROWTH_OUTPUT_PATH}`")
    print(growth_df)

if __name__ == "__main__":
    load_and_prepare_ytd_growth()
