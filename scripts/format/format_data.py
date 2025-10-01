import sys
import os
import pandas as pd

# Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.date_utils import get_key_dates  # Import date logic

def format_data(file_path, output_csv):
    """
    Loads Excel data, formats it, and saves it as a CSV.
    If the file already exists, it will be replaced.
    """
    print(f"\n🔄 Processing file: {file_path}")

    # Ensure the file exists before proceeding
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found - {file_path}")
        return None

    # Load Excel file
    df = pd.read_excel(file_path, sheet_name="Sheet1")
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date  # Convert to date-only format

    # Retrieve key dates from date_utils.py
    key_dates = get_key_dates()
    last_sunday = key_dates["last_sunday"]
    eight_weeks_back = key_dates["eight_weeks_back"]
    fiscal_start = key_dates["fiscal_start"]
    quarter_start = key_dates["quarter_start"]
    month_start = key_dates["month_start"]
    current_year = key_dates["current_year"]

    # Add classification columns
    df['CurrentWeeks'] = df['Date'].apply(lambda x: "TRUE" if eight_weeks_back <= x <= last_sunday else "FALSE")
    df['YTD'] = df['Date'].apply(lambda x: "TRUE" if fiscal_start <= x <= last_sunday else "FALSE")
    df['CurrentQuarter'] = df['Date'].apply(lambda x: "TRUE" if quarter_start <= x <= last_sunday else "FALSE")
    df['CurrentMonth'] = df['Date'].apply(lambda x: "TRUE" if month_start <= x <= last_sunday else "FALSE")

    # Year Classification
    df['YEAR2'] = df['Date'].apply(lambda x: 
        "current" if x.year == current_year else 
        "Last" if x.year == current_year - 1 else 
        "Last-1" if x.year == current_year - 2 else 
        "null"
    )

    # Ensure output directory exists
    output_dir = os.path.dirname(output_csv)
    os.makedirs(output_dir, exist_ok=True)

    # Remove existing file if necessary
    if os.path.exists(output_csv):
        print(f"🔄 File {output_csv} already exists. Replacing it.")
        os.remove(output_csv)

    # Save formatted data
    df.to_csv(output_csv, index=False, na_rep="null")
    print(f"✅ Data formatted and saved to {output_csv}")

    # Debugging: Print YEAR2 classification counts
    print("\n📊 YEAR2 Classification Counts:")
    print(df['YEAR2'].value_counts(dropna=False))  # Ensures null values are counted

    return df  # Return DataFrame for further processing

# Run the script if executed directly
if __name__ == "__main__":
    file_path = "/Users/axelsamuelson/Documents/CDLP_code/weekly_reports/data/Weekly_Data.xlsx"
    output_csv = "/Users/axelsamuelson/Documents/CDLP_code/weekly_reports/data"
