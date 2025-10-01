import sys
import os
import pandas as pd
from datetime import datetime

# ✅ Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Import function to get last 8 weeks
from calculator.date_utils import get_last_8_weeks

# ✅ Define file paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INPUT_FILE = os.path.join(BASE_DIR, "data", "raw", "sessions_markets_raw.csv")
CSV_OUTPUT_FILE = os.path.join(BASE_DIR, "data", "final", "sessions_markets_final.csv")

# ✅ Ensure output directory exists
os.makedirs(os.path.dirname(CSV_OUTPUT_FILE), exist_ok=True)


def format_sessions_data(df):
    """
    Formats sessions data with appropriate decimal handling:
    - Sessions → 1 decimal in thousands (e.g., 1.5 for 1500 sessions)
    """

    print("\n🔍 **Step 1: Raw 'Value' Column Before Formatting**")
    print(df[["Market", "Value"]].head(10))  # Inspect raw values

    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")  # Ensure numeric values

    def apply_formatting(row):
        """Applies formatting for sessions data."""
        original_value = row["Value"]  # Keep original for logging
        
        # Sessions: 1 decimal in thousands
        formatted_value = round(row["Value"] / 1000, 1)  # Convert to thousands with 1 decimal

        # Log transformation for debugging
        print(f"🔄 Formatting '{row['Market']}': {original_value} → {formatted_value}")
        return formatted_value

    df["Value"] = df.apply(apply_formatting, axis=1)

    print("\n🔍 **Step 2: 'Value' Column After Formatting**")
    print(df[["Market", "Value"]].head(10))  # Inspect transformed values

    return df


def sort_and_save_sessions_data(input_file, csv_output):
    """Loads sessions data, sorts it based on the last 8 weeks, formats it, and saves as CSV."""

    # ✅ Load the dataset
    try:
        df = pd.read_csv(input_file, sep=";", decimal=",")
    except FileNotFoundError:
        print(f"❌ File not found: {input_file}. Please check the path and try again.")
        return
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return

    # ✅ Verify necessary columns exist
    required_columns = {"Calendar Year", "ISO Week", "Market", "Value", "Year Type"}
    if not required_columns.issubset(df.columns):
        print(f"❌ Missing required columns: {required_columns - set(df.columns)}")
        return

    print("\n📊 **Step 0: Raw Data Loaded**")
    print(df.head(10))

    # ✅ Apply formatting BEFORE pivoting
    df = format_sessions_data(df)

    # ✅ Get last 8 weeks in correct order (newest first, oldest last)
    last_8_weeks, _ = get_last_8_weeks()
    last_8_weeks_order = [
        (week["week_start"].year, week["week_start"].isocalendar()[1]) for week in reversed(last_8_weeks)
    ]

    print("\n📆 **Step 3: Expected Week Order (newest → oldest):**", last_8_weeks_order)

    # ✅ Assign sorting order based on the correct week order
    df["SortOrder"] = df.apply(
        lambda row: last_8_weeks_order.index((row["Calendar Year"], row["ISO Week"]))
        if (row["Calendar Year"], row["ISO Week"]) in last_8_weeks_order else float("inf"),
        axis=1
    )

    # ✅ Sort data based on the last 8 weeks order
    df_sorted = df.sort_values(by="SortOrder").drop(columns=["SortOrder"])

    print("\n📊 **Step 4: Sorted Sessions Data Before Pivoting**")
    print(df_sorted.head(10))

    # ✅ Pivot table to have weeks as columns (newest → oldest)
    df_pivot = df_sorted.pivot_table(
        index=["Market", "Year Type"], 
        columns="ISO Week", 
        values="Value", 
        aggfunc="first"
    ).reset_index()

    # ✅ Reorder the week columns from newest to oldest
    iso_weeks_sorted = [week[1] for week in last_8_weeks_order]
    df_pivot = df_pivot[["Market", "Year Type"] + iso_weeks_sorted]

    print("\n📊 **Step 5: Sessions Data After Pivoting**")
    print(df_pivot.head(10))

    # ✅ Force final formatting after pivoting
    for col in iso_weeks_sorted:
        if col in df_pivot.columns:
            df_pivot[col] = df_pivot.apply(
                lambda row: round(row[col], 1) if pd.notna(row[col]) else row[col],
                axis=1
            )

    print("\n📊 **Step 6: Sessions Data After Final Formatting**")
    print(df_pivot.head(10))

    # ✅ Display full DataFrame in terminal
    pd.set_option("display.max_rows", None)
    pd.set_option("display.float_format", lambda x: f"{x:.1f}" if isinstance(x, float) else str(int(x)))

    print("\n📊 **Final Formatted Sessions Data:**")
    print(df_pivot.to_string(index=False))  # Display full DataFrame in readable format

    # ✅ Save the sorted and formatted data as a CSV file
    df_pivot.to_csv(csv_output, index=False)

    print(f"\n✅ Successfully saved formatted sessions data to CSV: {csv_output}")


# ✅ Run the script
if __name__ == "__main__":
    sort_and_save_sessions_data(INPUT_FILE, CSV_OUTPUT_FILE)
