import os
import pandas as pd

# Define paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
FINAL_DATA_DIR = os.path.join(BASE_DIR, "data", "final")

# Ensure final data directory exists
os.makedirs(FINAL_DATA_DIR, exist_ok=True)

# Define input/output paths
YTD_GROWTH_RAW_PATH = os.path.join(RAW_DATA_DIR, "ytd_growth_metrics_raw.csv")
YTD_GROWTH_FINAL_PATH = os.path.join(FINAL_DATA_DIR, "ytd_growth_final.csv")

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

# Define correct column order
COLUMN_ORDER = ["ytd_last_year", "ytd_two_years", "budget", "budget_vs_last_year"]

def format_growth(value):
    """
    Formats growth values:
    - Converts negative values (e.g., `-11.4%`) into parentheses format `(11.4%)`
    - Leaves positive values unchanged (e.g., `8.2%`)
    - Replaces missing values ("N/A", "n/m", "0") with "-"
    """
    if pd.isna(value) or value in ["N/A", "n/m", "0"]:
        return "-"

    # Ensure value is a string and remove any unintended characters
    value = str(value).replace(",", "").strip()

    # Convert to float for processing
    try:
        value = float(value.replace("%", ""))
    except ValueError:
        return value  # Return as-is if conversion fails

    # Apply formatting
    if value < 0:
        return f"({abs(value)}%)"  # Convert -11.4% to (11.4%)
    else:
        return f"{value}%"  # Leave positive values unchanged

def finalize_ytd_growth():
    """Loads, filters, formats, and saves the finalized Fiscal YTD Growth file."""
    # Load raw YTD growth data
    df = pd.read_csv(YTD_GROWTH_RAW_PATH, index_col=0)

    # **Filter Only Required Metrics**
    df = df.loc[METRIC_NAMES]  # Keep only specified metrics

    # **Reorder columns**
    df = df[COLUMN_ORDER]  # Reorder columns correctly

    # Debugging: Print raw DataFrame before formatting
    print("\n🔍 **Raw YTD Growth Data Before Formatting:**")
    print(df)  # Print full table

    # Apply growth formatting
    df = df.applymap(format_growth)

    # Debugging: Print formatted DataFrame after formatting
    print("\n✅ **Formatted YTD Growth Data After Formatting:**")
    print(df)  # Print full table

    # Save formatted Fiscal YTD Growth data
    df.to_csv(YTD_GROWTH_FINAL_PATH, index=True)

    print(f"\n✅ Finalized Fiscal YTD Growth Data saved to `{YTD_GROWTH_FINAL_PATH}`")

if __name__ == "__main__":
    finalize_ytd_growth()
