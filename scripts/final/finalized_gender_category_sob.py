import sys
import os
import pandas as pd

# ✅ Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Define file paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CURRENT_YEAR_FILE = os.path.join(BASE_DIR, "data", "final", "gender_category_final.csv")
CSV_OUTPUT_FILE = os.path.join(BASE_DIR, "data", "final", "gender_category_sob_final.csv")

# ✅ Ensure output directory exists
os.makedirs(os.path.dirname(CSV_OUTPUT_FILE), exist_ok=True)


def load_and_prepare_data():
    """Loads and prepares the finalized gender-category revenue data for share calculation."""
    try:
        df_current = pd.read_csv(CURRENT_YEAR_FILE)
    except FileNotFoundError as e:
        print(f"❌ File not found: {e.filename}")
        return None, None
    except Exception as e:
        print(f"❌ An error occurred while loading the file: {e}")
        return None, None

    # ✅ Identify numeric week columns (ISO week numbers)
    week_columns = [col for col in df_current.columns if col.isdigit()]

    # ✅ Ensure required columns exist
    required_columns = set(week_columns + ["8-week avg", "Gender", "Category"])
    if not required_columns.issubset(df_current.columns):
        print(f"❌ Missing required columns in the file: {required_columns}")
        return None, None

    print("\n📊 **Step 1: Loaded Data from Current Year**")
    print(f"Current Year Data: {df_current.shape}")

    return df_current, week_columns


def calculate_share(df_current, week_columns):
    """Calculates the share of revenue for each category based on the grand total row stored in the 'Gender' column."""

    # ✅ **Locate Grand Total row (Stored under 'Gender')**
    grand_total_row = df_current[df_current["Gender"] == "Grand Total"]

    if grand_total_row.empty:
        print("❌ No 'Grand Total' row found in Gender column! Exiting...")
        return None

    # ✅ Extract numeric values for the grand total
    grand_total_values = grand_total_row[week_columns + ["8-week avg"]].iloc[0]

    # ✅ Debugging print: Show extracted Grand Total values
    print("\n📊 **Extracted Grand Total Per Week (From 'Gender' Column):**")
    print(grand_total_values)

    # ✅ Compute share by dividing each revenue value by the **Grand Total per week**
    df_share = df_current.copy()
    
    for week in week_columns + ["8-week avg"]:
        df_share[week] = (df_share[week] / grand_total_values[week]) * 100  # Convert to percentage

    # ✅ Keep only relevant columns (Gender, Category, Share Values)
    share_columns = ["Gender", "Category"] + week_columns + ["8-week avg"]
    df_share = df_share[share_columns]

    print("\n📊 **Step 2: Calculated Share of Revenue (With Gender & Category)**")
    print(df_share.to_string(index=False))

    return df_share


def validate_total(df_share, week_columns):
    """Ensures the total per week sums to ~100% (Column-Wise)."""
    total_check = df_share[week_columns + ["8-week avg"]].sum()
    print("\n✅ **Total Sum for Each Week (Should be 100% per column now!):**")
    print(total_check)


def format_output(df_share):
    """Formats numbers as percentages and replaces zero/NaN with '-'."""
    for col in df_share.columns[2:]:  # Skip Gender & Category columns
        df_share[col] = df_share[col].apply(
            lambda x: "-" if pd.isna(x) or x == 0 else f"{round(x)}%"
        )
    return df_share


def save_to_csv(df_share, output_file):
    """Saves the final processed Share DataFrame to CSV."""
    df_share.to_csv(output_file, index=False)
    print(f"\n✅ Successfully saved Gender & Category Share data to CSV: {output_file}")


def process_gender_category_share():
    """Runs the full pipeline: Load → Calculate Share → Validate → Print → Save."""

    # ✅ Load and prepare the data
    df_current, week_columns = load_and_prepare_data()
    if df_current is None:
        print("❌ No data available for processing. Exiting...")
        return

    # ✅ Calculate Share of Revenue
    df_share = calculate_share(df_current, week_columns)
    if df_share is None:
        print("❌ Error in calculating share. Exiting...")
        return

    # ✅ Validate that total per week sums to **100%** (Column-Wise)
    validate_total(df_share, week_columns)

    # ✅ Format output
    df_share_formatted = format_output(df_share)

    # ✅ Print formatted DataFrame
    print("\n📊 **Step 3: Final Share Data (Formatted as Percentages)**")
    print(df_share_formatted.to_string(index=False))

    # ✅ Drop Gender & Category Columns for final output
    df_share_no_labels = df_share_formatted.drop(columns=["Gender", "Category"], errors="ignore")

    # ✅ Save final output
    save_to_csv(df_share_no_labels, CSV_OUTPUT_FILE)


# ✅ Run the script
if __name__ == "__main__":
    process_gender_category_share()