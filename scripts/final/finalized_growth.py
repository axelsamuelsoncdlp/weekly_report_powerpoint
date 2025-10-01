import os
import pandas as pd

# Define paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
FINAL_DATA_DIR = os.path.join(BASE_DIR, "data", "final")

# Ensure final data directory exists
os.makedirs(FINAL_DATA_DIR, exist_ok=True)

# Define input/output paths
GROWTH_RAW_PATH = os.path.join(RAW_DATA_DIR, "growth_metrics_raw.csv")
GROWTH_FINAL_PATH = os.path.join(FINAL_DATA_DIR, "growth_metrics_final.csv")

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

# Define the correct column order
EXPECTED_COLUMNS = ["last_week", "last_year", "year_2023", "Budget(1)"]

def format_growth(value):
    """
    Formats growth values:
    - Converts negative values (e.g., `-11.4%`) into parentheses format `(11.4%)`
    - Leaves positive values unchanged (e.g., `8.2%`)
    - Ensures `n/m` values remain unchanged
    """
    if pd.isna(value) or value == "n/m":
        return "n/m"

    # Ensure value is a string and remove any unintended characters
    value = str(value).replace(",", "").strip()

    # Convert to float for processing
    try:
        value = float(value.replace("%", ""))
    except ValueError:
        return value  # Return as-is if conversion fails

    # Apply formatting
    if value < 0:
        return f"({abs(value):.1f}%)"  # Convert -11.4% to (11.4%)
    else:
        return f"{value:.1f}%"  # Format with one decimal

def finalize_growth():
    """Loads, filters, formats, and saves the finalized growth data file."""
    # Load raw growth data
    df = pd.read_csv(GROWTH_RAW_PATH, index_col=0)

    # Filter only required metrics
    df = df.loc[METRIC_NAMES]

    # Apply growth formatting
    for column in df.columns:
        for metric in df.index:
            df.at[metric, column] = format_growth(df.at[metric, column])

    # Reorder columns
    df = df[EXPECTED_COLUMNS]

    # Debugging: Print formatted growth metrics
    print("\n✅ **Final Growth Data After Formatting & Column Reorder:**")
    print(df.to_string())

    # Save formatted growth data
    df.to_csv(GROWTH_FINAL_PATH, index=True)

    print(f"\n✅ Finalized Growth Data saved to `{GROWTH_FINAL_PATH}`")

if __name__ == "__main__":
    finalize_growth()
