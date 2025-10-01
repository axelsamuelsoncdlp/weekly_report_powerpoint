import sys
import os
import pandas as pd

# Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.metrics_calculator import calculate_growth

# Define file paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))  
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")  
METRICS_INPUT_PATH = os.path.join(RAW_DATA_DIR, "metrics_raw.csv")  
GROWTH_OUTPUT_PATH = os.path.join(RAW_DATA_DIR, "growth_metrics_raw.csv")  

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

def load_and_prepare_growth():
    """Computes and saves growth metrics for Last Week, Last Year, and 2023."""
    # Ensure the raw data directory exists
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # Load raw revenue & cost metrics
    metrics_df = pd.read_csv(METRICS_INPUT_PATH, index_col=0)

    # Debugging: Check structure of DataFrame
    print("\n🔍 Debug: Metrics DataFrame Structure")
    print(metrics_df.head())
    print("🔍 Columns:", metrics_df.columns.tolist())
    print("🔍 Index:", metrics_df.index.tolist())

    # Initialize dictionary for storing growth calculations
    growth_data = {metric: {} for metric in METRIC_NAMES}

    for metric in METRIC_NAMES:
        try:
            # Get values safely, defaulting to "N/A" if missing
            current_week = metrics_df.at[metric, "current_week"] if metric in metrics_df.index else "N/A"
            last_week = metrics_df.at[metric, "last_week"] if metric in metrics_df.index else "N/A"
            last_year = metrics_df.at[metric, "last_year"] if metric in metrics_df.index else "N/A"
            year_2023 = metrics_df.at[metric, "year_2023"] if metric in metrics_df.index else "N/A"

            # Convert values to float for calculations
            if current_week != "N/A" and last_week != "N/A":
                growth_data[metric]["last_week"] = calculate_growth(float(current_week), float(last_week))
            else:
                growth_data[metric]["last_week"] = "N/A"

            if current_week != "N/A" and last_year != "N/A":
                growth_data[metric]["last_year"] = calculate_growth(float(current_week), float(last_year))
            else:
                growth_data[metric]["last_year"] = "N/A"

            if current_week != "N/A" and year_2023 != "N/A":
                growth_data[metric]["year_2023"] = calculate_growth(float(current_week), float(year_2023))
            else:
                growth_data[metric]["year_2023"] = "N/A"

        except Exception as e:
            print(f"⚠️ Error calculating growth for {metric}: {e}")
            growth_data[metric]["last_week"] = "N/A"
            growth_data[metric]["last_year"] = "N/A"
            growth_data[metric]["year_2023"] = "N/A"

    # Convert to DataFrame
    growth_df = pd.DataFrame.from_dict(growth_data, orient="index")

    # Ensure correct column order and add missing columns
    growth_df["Budget(1)"] = "n/m"
    growth_df = growth_df[["last_week", "last_year", "Budget(1)", "year_2023"]]

    # Ensure output directory exists before saving
    os.makedirs(os.path.dirname(GROWTH_OUTPUT_PATH), exist_ok=True)

    # Save growth metrics
    growth_df.to_csv(GROWTH_OUTPUT_PATH, index=True)

    print(f"\n✅ Growth Metrics saved to `{GROWTH_OUTPUT_PATH}`")
    print(growth_df)

if __name__ == "__main__":
    load_and_prepare_growth()