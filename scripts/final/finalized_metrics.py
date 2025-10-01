import sys
import os
import pandas as pd

# Add the scripts folder to Python's import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Define file paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))  
RAW_METRICS_PATH = os.path.join(BASE_DIR, "data", "raw", "metrics_raw.csv")
FINAL_METRICS_PATH = os.path.join(BASE_DIR, "data", "final", "metrics_final.csv")

# Define required metrics
METRIC_NAMES = [
    "Online Gross Revenue",
    "Returns",
    "Return rate %",
    "Online Net Revenue",
    "Retail Concept Store",
    "Retail Pop-ups, Outlets",
    "Retail Net Revenue",
    "Wholesale Net Revenue",
    "Total Net Revenue",
    "Returning Customers",
    "New Customers",
    "Marketing Spend",
    "Online Cost of Sale (CoS)",
]

# Define required columns (including last_year & year_2023)
EXPECTED_COLUMNS = ["current_week", "last_week", "last_year", "year_2023"]

# Metrics that should be formatted in thousands
THOUSANDS_METRICS = [
    "Online Gross Revenue",
    "Returns",
    "Online Net Revenue",
    "Retail Concept Store",
    "Retail Pop-ups, Outlets",
    "Retail Net Revenue",
    "Wholesale Net Revenue",
    "Total Net Revenue",
    "Marketing Spend",  # ✅ Added Marketing Spend
]

# Metrics that should have one decimal and a percentage sign
PERCENTAGE_METRICS = ["Online Cost of Sale (CoS)", "Return rate %"]

def format_metrics(df):
    """Formats numbers properly in the DataFrame while keeping them as strings."""
    # Convert all numeric data to float where possible, but keep existing strings
    for metric in df.index:
        if metric in PERCENTAGE_METRICS:
            df.loc[metric] = df.loc[metric].apply(
                lambda x: f"{round(float(x), 1)} %" if pd.notna(x) and str(x).replace('.', '', 1).isdigit() else x
            )
        elif metric in THOUSANDS_METRICS:
            df.loc[metric] = df.loc[metric].apply(
                lambda x: f"{int(round(float(x) / 1000)):,}" if pd.notna(x) and str(x).replace('.', '', 1).isdigit() else x
            )
        elif metric in ["Returning Customers", "New Customers"]:
            df.loc[metric] = df.loc[metric].apply(
                lambda x: f"{int(round(float(x))):,}" if pd.notna(x) and str(x).replace(',', '').isdigit() else x
            )
        else:
            df.loc[metric] = df.loc[metric].apply(
                lambda x: f"{int(round(float(x))):,}" if pd.notna(x) and str(x).replace(',', '').isdigit() else x
            )

    return df

def load_and_prepare_finalized_data():
    """Extracts and saves the required metrics from metrics_raw.csv to metrics_final.csv."""

    # Load raw metrics
    metrics_df = pd.read_csv(RAW_METRICS_PATH, index_col=0, dtype=str)  # ✅ Keep as strings

    # Ensure all expected columns are present, even if they don't exist in the raw data
    for col in EXPECTED_COLUMNS:
        if col not in metrics_df.columns:
            metrics_df[col] = "n/m"  # Fill missing columns with "n/m"

    # Filter only the required metrics and available columns
    metrics_df = metrics_df.loc[METRIC_NAMES, EXPECTED_COLUMNS]

    # Format numbers properly
    metrics_df = format_metrics(metrics_df)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(FINAL_METRICS_PATH), exist_ok=True)

    # Save finalized metrics as strings to maintain formatting
    metrics_df.to_csv(FINAL_METRICS_PATH, index=True)
    print(f"✅ Finalized Metrics saved to `{FINAL_METRICS_PATH}`")
    print(metrics_df)  # Debug output to verify

if __name__ == "__main__":
    load_and_prepare_finalized_data()
