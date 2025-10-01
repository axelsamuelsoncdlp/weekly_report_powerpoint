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
INPUT_FILE = os.path.join(BASE_DIR, "data", "raw", "women_category_revenue_raw.csv")
CSV_OUTPUT_FILE = os.path.join(BASE_DIR, "data", "final", "women_category_revenue_final.csv")

# ✅ Ensure output directory exists
os.makedirs(os.path.dirname(CSV_OUTPUT_FILE), exist_ok=True)


def merge_categories(df):
    """Merges 'Poolwear' and 'Swimwear' into 'Swim & Pool' and ensures correct formatting."""

    print("\n🔍 **Step 1: Raw Data Before Merging Categories**")
    print(df[["Product Category", "Value"]].head(10))  # Inspect raw values

    # ✅ Merge categories
    category_mapping = {
        "POOLWEAR": "Swim & Pool",
        "SWIMWEAR": "Swim & Pool"
    }
    df["Product Category"] = df["Product Category"].replace(category_mapping)

    # ✅ Aggregate values after merging categories
    df = df.groupby(["Year Type", "Calendar Year", "ISO Week", "Gender", "Product Category"], as_index=False)["Value"].sum()

    print("\n📊 **Step 2: Data After Merging Categories**")
    print(df[["Product Category", "Value"]].head(10))  # Inspect transformed values

    return df


def sort_and_save_women_category_data(input_file, csv_output):
    """Loads Women Category Revenue data, merges categories, sorts it, and saves as CSV."""

    # ✅ Load the dataset
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"❌ File not found: {input_file}. Please check the path and try again.")
        return
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return

    # ✅ Verify necessary columns exist
    required_columns = {"Calendar Year", "ISO Week", "Gender", "Product Category", "Value", "Year Type"}
    if not required_columns.issubset(df.columns):
        print(f"❌ Missing required columns: {required_columns - set(df.columns)}")
        return

    print("\n📊 **Step 0: Raw Data Loaded**")
    print(df.head(10))

    # ✅ Replace NaN or missing values in critical columns
    df.fillna({"Gender": "WOMEN", "Product Category": "UNKNOWN", "Value": 0}, inplace=True)

    # ✅ Convert 'Value' column to numeric (ensure it's valid)
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce").fillna(0).astype(int)

    # ✅ Merge categories before formatting
    df = merge_categories(df)

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

    print("\n📊 **Step 4: Sorted Women Category Revenue Data Before Pivoting**")
    print(df_sorted.head(10))

    # ✅ Pivot table to have weeks as columns (newest → oldest)
    df_pivot = df_sorted.pivot_table(
        index=["Gender", "Product Category", "Year Type"], 
        columns="ISO Week", 
        values="Value", 
        aggfunc="sum"
    ).reset_index()

    # ✅ Replace NaN values in pivot table with 0
    df_pivot.fillna(0, inplace=True)

    # ✅ Reorder the week columns from newest to oldest
    iso_weeks_sorted = [week[1] for week in last_8_weeks_order]
    df_pivot = df_pivot[["Gender", "Product Category", "Year Type"] + iso_weeks_sorted]

    print("\n📊 **Step 5: Women Category Revenue Data After Pivoting**")
    print(df_pivot.head(20))

    # ✅ Save the sorted and formatted data as a CSV file
    df_pivot.to_csv(csv_output, index=False)

    print(f"\n✅ Successfully saved formatted Women Category Revenue data to CSV: {csv_output}")


# ✅ Run the script
if __name__ == "__main__":
    sort_and_save_women_category_data(INPUT_FILE, CSV_OUTPUT_FILE)