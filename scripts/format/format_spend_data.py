import os
import pandas as pd
from datetime import datetime, timedelta

# ✅ Define paths
BASE_DIR = "/Users/axelsamuelson/Documents/CDLP_CODE/weekly_reports_powerpoint"
UNFORMATTED_DIR = os.path.join(BASE_DIR, "data/Marketing Spend/unformatted")
FORMATTED_DIR = os.path.join(BASE_DIR, "data/formatted")

MERGED_CSV_FILE = os.path.join(FORMATTED_DIR, "marketing_spend_merged.csv")  # Merged raw data
FORMATTED_CSV_FILE = os.path.join(FORMATTED_DIR, "marketing_spend_formatted.csv")  # Final formatted dataset

# ✅ Ensure output directory exists
os.makedirs(FORMATTED_DIR, exist_ok=True)

# ✅ Expected column names (keeping only relevant ones)
EXPECTED_COLUMNS = ["Market", "Date", "Total Spend", "Ad Spend", "FB Spend"]
KEEP_COLUMNS = ["Market", "Date", "Total Spend"]  # ✅ Only keep these

def get_week_ranges():
    """Returns start and end dates for Current Week, Last Week, Last Year, and 2023."""
    today = datetime.today()

    # ✅ Current Week (Monday-Sunday)
    current_sunday = today - timedelta(days=today.weekday() + 1)
    current_monday = current_sunday - timedelta(days=6)

    # ✅ Last Week (Previous Monday-Sunday)
    last_sunday = current_monday - timedelta(days=1)
    last_monday = last_sunday - timedelta(days=6)

    # ✅ Last Year (Same week last year)
    last_year_monday = last_monday - timedelta(weeks=52)
    last_year_sunday = last_sunday - timedelta(weeks=52)

    # ✅ 2023 (Same week in 2023)
    year_2023_monday = last_year_monday - timedelta(weeks=52)
    year_2023_sunday = last_year_sunday - timedelta(weeks=52)

    return {
        "current_week": (current_monday.date(), current_sunday.date()),
        "last_week": (last_monday.date(), last_sunday.date()),
        "last_year": (last_year_monday.date(), last_year_sunday.date()),
        "year_2023": (year_2023_monday.date(), year_2023_sunday.date()),
    }

def clean_numeric_values(df, column_name):
    """Converts values to numeric, handling potential formatting issues."""
    df[column_name] = df[column_name].astype(str).str.replace(',', '', regex=True)
    df[column_name] = pd.to_numeric(df[column_name], errors="coerce").fillna(0)
    return df

def load_and_clean_spend_data():
    """Reads, cleans, and processes marketing spend data (keeping all data)."""
    all_dataframes = []
    error_files = []

    # ✅ Load all CSV files in the unformatted directory
    for filename in sorted(os.listdir(UNFORMATTED_DIR)):
        if filename.endswith(".csv"):
            file_path = os.path.join(UNFORMATTED_DIR, filename)

            try:
                df = pd.read_csv(file_path, header=None, names=EXPECTED_COLUMNS, skiprows=1, na_values=["#N/A"], low_memory=False)

                # ✅ Keep only required columns
                df = df[KEEP_COLUMNS]

                # ✅ Convert Date column to datetime
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
                df = df.dropna(subset=["Date"])  # Drop rows with missing dates

                # ✅ Ensure numeric formatting for Total Spend
                df = clean_numeric_values(df, "Total Spend")

                all_dataframes.append(df)

            except Exception as e:
                error_files.append((filename, str(e)))
                print(f"❌ Error loading {filename}: {e}")

    if not all_dataframes:
        print("⚠️ No valid files found. Please check the directory and file formats.")
        return

    # ✅ Merge all data (without removing duplicates)
    merged_df = pd.concat(all_dataframes, ignore_index=True)
    merged_df.to_csv(MERGED_CSV_FILE, index=False)
    print(f"\n📂 **Saved merged data (without duplicate removal) to:** {MERGED_CSV_FILE}")

    # ✅ Save the merged dataset as the final dataset (all data kept)
    merged_df.to_csv(FORMATTED_CSV_FILE, index=False)
    print(f"\n✅ **Final processed data saved to:** {FORMATTED_CSV_FILE}")

    # ✅ Display debugging info
    print("\n📊 **Summary of Final Spend Data:**")
    print(f"📅 Earliest Date: {merged_df['Date'].min().strftime('%Y-%m-%d')}")
    print(f"📅 Latest Date: {merged_df['Date'].max().strftime('%Y-%m-%d')}")
    print(f"🔢 Total Rows: {len(merged_df):,}")
    print(f"🔍 Unique Dates: {merged_df['Date'].nunique()}")

    # ✅ Fetch week ranges
    week_ranges = get_week_ranges()

    # ✅ Calculate total spend for each week
    spend_summaries = {}
    for label, (week_start, week_end) in week_ranges.items():
        week_df = merged_df[(merged_df["Date"] >= week_start) & (merged_df["Date"] <= week_end)]
        total_spend = week_df["Total Spend"].sum()  # ✅ Correctly summing Total Spend
        spend_summaries[label] = total_spend

        # ✅ Debugging: Print spend breakdown for last week
        if label == "last_week":
            print("\n🔎 **DEBUG: Checking Last Week Spend Calculation**")
            print(f"📅 **Last Week Range:** {week_start} - {week_end}")
            print(f"🔢 **Unique Dates Found:** {week_df['Date'].nunique()} (should be 7)")
            print(f"💰 **Total Spend Last Week:** {round(total_spend)}")
            print("\n📝 **First 5 Rows from Last Week Data:**")
            print(week_df.head())

    # ✅ Print Spend Summary
    print("\n💰 **Marketing Spend Summary (All Entries Kept):**")
    print(f"📅 **Current Week ({week_ranges['current_week'][0]} - {week_ranges['current_week'][1]}):** {round(spend_summaries['current_week'])}")
    print(f"📅 **Last Week ({week_ranges['last_week'][0]} - {week_ranges['last_week'][1]}):** {round(spend_summaries['last_week'])}")
    print(f"📅 **Last Year ({week_ranges['last_year'][0]} - {week_ranges['last_year'][1]}):** {round(spend_summaries['last_year'])}")
    print(f"📅 **Year 2023 ({week_ranges['year_2023'][0]} - {week_ranges['year_2023'][1]}):** {round(spend_summaries['year_2023'])}")

    # 🚨 Display any errors
    if error_files:
        print("\n🚨 **Errors encountered in the following files:**")
        for filename, error_msg in error_files:
            print(f"❌ {filename}: {error_msg}")

if __name__ == "__main__":
    load_and_clean_spend_data()
