import os
import pandas as pd
from datetime import datetime, timedelta

# Define paths
BASE_DIR = "/Users/axelsamuelson/Documents/CDLP_CODE/weekly_reports_powerpoint"
UNFORMATTED_DIR = os.path.join(BASE_DIR, "data/Marketing Spend/unformatted")

# Expected column names
EXPECTED_COLUMNS = ["Market", "Date", "Total Spend", "Ad Spend", "FB Spend"]

# Define a function to get the latest full ISO week
def get_week_ranges():
    # Import the consistent date logic from date_utils
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from calculator.date_utils import get_latest_full_week
    
    return get_latest_full_week()

def clean_numeric_values(df, column_name):
    """Convert values to numeric and handle formatting issues."""
    df[column_name] = df[column_name].astype(str).str.replace(',', '', regex=True)
    df[column_name] = pd.to_numeric(df[column_name], errors="coerce").fillna(0)
    return df

def load_and_audit_spend_data():
    """Loads all marketing spend data and audits for duplicates and inconsistencies."""
    all_dataframes = []
    error_files = []

    # Iterate through all CSV files in the unformatted directory
    for filename in sorted(os.listdir(UNFORMATTED_DIR)):
        if filename.endswith(".csv"):
            file_path = os.path.join(UNFORMATTED_DIR, filename)

            try:
                # Load CSV
                df = pd.read_csv(file_path, header=None, names=EXPECTED_COLUMNS, skiprows=1, na_values=["#N/A"], low_memory=False)

                # Convert Date column to datetime
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

                # Drop invalid/missing dates
                df = df.dropna(subset=["Date"])

                # Ensure numeric formatting for Total Spend column only
                df = clean_numeric_values(df, "Total Spend")

                # Store dataframe
                all_dataframes.append(df)

            except Exception as e:
                error_files.append((filename, str(e)))
                print(f"❌ Error loading {filename}: {e}")

    if not all_dataframes:
        print("⚠️ No valid files found. Please check the directory and file formats.")
        return

    # Combine all dataframes
    final_df = pd.concat(all_dataframes, ignore_index=True)

    # **Audit 1️⃣: Check for Duplicate Rows (Market + Date)**
    duplicate_rows = final_df[final_df.duplicated(subset=["Market", "Date"], keep=False)]
    print("\n🔍 **Duplicate Rows (Market + Date):**")
    if duplicate_rows.empty:
        print("✅ No duplicates found at Market + Date level.")
    else:
        print(duplicate_rows)

    # **Audit 2️⃣: Check for Incorrect Data Formatting**
    print("\n📊 **Data Formatting Summary:**")
    print(f"📅 Date Range: {final_df['Date'].min()} → {final_df['Date'].max()}")
    print(f"🔢 Unique Markets: {final_df['Market'].nunique()}")
    print(f"💰 Total Spend (Sum): {final_df['Total Spend'].sum():,.2f}")
    print(f"📊 Dataset Size: {final_df.shape[0]} rows")

    # **Audit 3️⃣: Weekly Summaries**
    week_ranges = get_week_ranges()

    for period, (start, end) in week_ranges.items():
        period_df = final_df[(final_df["Date"] >= start) & (final_df["Date"] <= end)]
        total_spend = period_df["Total Spend"].sum()
        print(f"📅 **{period.replace('_', ' ').title()} ({start} - {end})**: {total_spend:,.2f}")

    # Save the audit output to CSV for review
    audit_output_path = os.path.join(BASE_DIR, "data/audit/spend_audit.csv")
    os.makedirs(os.path.dirname(audit_output_path), exist_ok=True)
    final_df.to_csv(audit_output_path, index=False)

    print(f"\n✅ Audit file saved to: {audit_output_path}")

    # Report errors if any
    if error_files:
        print("\n🚨 **Errors encountered in the following files:**")
        for filename, error_msg in error_files:
            print(f"❌ {filename}: {error_msg}")

if __name__ == "__main__":
    load_and_audit_spend_data()