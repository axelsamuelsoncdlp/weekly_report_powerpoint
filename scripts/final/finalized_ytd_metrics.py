import os
import pandas as pd

# Define paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
FINAL_DATA_DIR = os.path.join(BASE_DIR, "data", "final")

# Ensure final data directory exists
os.makedirs(FINAL_DATA_DIR, exist_ok=True)

# Define input/output paths
YTD_METRICS_RAW_PATH = os.path.join(RAW_DATA_DIR, "ytd_metrics_raw.csv")
YTD_METRICS_FINAL_PATH = os.path.join(FINAL_DATA_DIR, "ytd_metrics_final.csv")

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

# Define metric categories for formatting
PERCENTAGE_COLUMNS = ["Return rate %", "Online Cost of Sale (CoS)"]
COUNT_COLUMNS = ["Returning Customers", "New Customers"]

# Define required column order
COLUMN_ORDER = ["ytd_current_month", "ytd_last_year", "ytd_two_years", "Budget(1)"]

def format_value(value, metric_name):
    """
    Formats numerical values properly:
    - Revenue & Returns in thousands (e.g., `1,010`)
    - Percentages with one decimal and `%` (e.g., `22.2%`)
    - Customer counts remain unchanged as whole numbers (e.g., `350`)
    - Missing values replaced with `"-"`
    """

    if pd.isna(value) or value in ["N/A", "n/m", "-"]:
        return "-"

    # Convert to float if it's a string to avoid errors
    try:
        value = float(value)
    except ValueError:
        return value  # Return as-is if conversion fails

    # Apply formatting rules based on metric type
    if metric_name in PERCENTAGE_COLUMNS:
        return f"{value:.1f}%"  # One decimal for percentage
    elif metric_name in COUNT_COLUMNS:
        return f"{int(value)}"  # Whole numbers for Returning/New Customers
    else:
        return f"{int(round(value / 1000)):,}"  # Thousands format for revenue & spend

def finalize_ytd_metrics():
    """Loads, filters, formats, and saves the finalized Fiscal YTD data file."""
    # Load raw YTD metrics data
    df = pd.read_csv(YTD_METRICS_RAW_PATH, index_col=0)

    # Debugging: Print raw YTD metrics in DataFrame format
    print("\n🔍 **Raw YTD Metrics Data Before Filtering & Formatting:**")
    print(df)

    # Filter only required metrics
    df = df.loc[METRIC_NAMES]

    # Ensure "Budget(1)" column exists and add it if missing
    if "Budget(1)" not in df.columns:
        df["Budget(1)"] = "-"

    # Apply formatting
    for metric in df.index:
        df.loc[metric] = df.loc[metric].apply(lambda x: format_value(x, metric))

    # Reorder columns
    df = df[COLUMN_ORDER]

    # Debugging: Print formatted YTD metrics in DataFrame format
    print("\n✅ **Formatted YTD Metrics Data After Filtering & Formatting:**")
    print(df)

    # Save formatted Fiscal YTD data
    df.to_csv(YTD_METRICS_FINAL_PATH, index=True)
    
    print(f"\n✅ Finalized Fiscal YTD Data saved to `{YTD_METRICS_FINAL_PATH}`")

if __name__ == "__main__":
    finalize_ytd_metrics()
