import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.date_utils import get_last_8_weeks

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INPUT_FILE = os.path.join(BASE_DIR, "data", "raw", "online_media_spend_raw.csv")
CSV_OUTPUT_FILE = os.path.join(BASE_DIR, "data", "final", "online_media_spend_final.csv")

os.makedirs(os.path.dirname(CSV_OUTPUT_FILE), exist_ok=True)

def sort_and_save_online_media_spend_data(input_file, csv_output):
    try:
        # Read CSV file with semicolon separator
        df = pd.read_csv(input_file, sep=";", decimal=",")
    except FileNotFoundError:
        print(f"❌ File not found: {input_file}. Please check the path and try again.")
        return
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return

    required_columns = {"Calendar Year", "ISO Week", "Market", "Value", "Year Type"}
    if not required_columns.issubset(df.columns):
        print(f"❌ Missing required columns: {required_columns - set(df.columns)}")
        return

    print("\n📊 **Step 0: Raw Spend Data Loaded**")
    print(df.head(10))

    # Convert Value column to numeric for proper sorting
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    print("\n🔍 **Original Spend Values (No Formatting) - Sample:**")
    print(df[["Market", "Value"]].head(20))

    # Get week ordering (newest → oldest)
    last_8_weeks, _ = get_last_8_weeks()
    last_8_weeks_order = [
        (week["week_start"].year, week["week_start"].isocalendar()[1]) for week in reversed(last_8_weeks)
    ]

    print("\n📆 **Step 3: Expected Week Order (newest → oldest):**", last_8_weeks_order)

    # Sort data according to week order
    df["SortOrder"] = df.apply(
        lambda row: last_8_weeks_order.index((row["Calendar Year"], row["ISO Week"]))
        if (row["Calendar Year"], row["ISO Week"]) in last_8_weeks_order else float("inf"),
        axis=1
    )

    df_sorted = df.sort_values(by="SortOrder").drop(columns=["SortOrder"])

    print("\n📊 **Step 4: Sorted Spend Data Before Pivoting**")
    print(df_sorted.head(10))

    # Pivot the data
    df_pivot = df_sorted.pivot_table(
        index=["Market", "Year Type"],
        columns="ISO Week",
        values="Value",
        aggfunc="first"
    ).reset_index()

    # Get week columns in the correct order
    iso_weeks_sorted = [week[1] for week in last_8_weeks_order]
    df_pivot = df_pivot[["Market", "Year Type"] + iso_weeks_sorted]

    print("\n📊 **Step 5: Spend Data After Pivoting**")
    print(df_pivot.head(10))

    # Convert spend values to thousands (divide by 1000) for cleaner display
    for col in iso_weeks_sorted:
        if col in df_pivot.columns:
            df_pivot[col] = df_pivot[col].apply(
                lambda x: round(x / 1000, 1) if pd.notna(x) and x > 0 else 0
            )

    print("\n📊 **Step 6: Spend Data After Converting to Thousands**")
    print(df_pivot.head(10))

    # Set pandas display options for better readability
    pd.set_option("display.max_rows", None)
    pd.set_option("display.float_format", lambda x: f"{x:.1f}" if isinstance(x, float) else str(int(x)))

    print("\n📊 **Final Spend Data (In Thousands):**")
    print(df_pivot.to_string(index=False))

    # Save to CSV with point as decimal separator for better Excel compatibility
    df_pivot.to_csv(csv_output, index=False, sep=";", decimal=".")

    print(f"\n✅ Successfully saved formatted online media spend data to CSV: {csv_output}")
    print(f"📊 **Format:** Spend values converted to thousands (divide by 1000)")
    print(f"📊 **Examples:** $57,224 → 57.2, $1,970 → 2.0")

if __name__ == "__main__":
    sort_and_save_online_media_spend_data(INPUT_FILE, CSV_OUTPUT_FILE)
