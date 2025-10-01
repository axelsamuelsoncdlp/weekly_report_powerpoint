import sys
import os
import pandas as pd
from datetime import datetime

# ✅ Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Import function to get last 8 weeks from last year
from calculator.date_utils import get_last_8_weeks_last_year

# ✅ Define file paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INPUT_FILE = os.path.join(BASE_DIR, "data", "raw", "gender_category_ly_raw.csv")
CSV_OUTPUT_FILE = os.path.join(BASE_DIR, "data", "final", "gender_category_ly_final.csv")

# ✅ Ensure output directory exists
os.makedirs(os.path.dirname(CSV_OUTPUT_FILE), exist_ok=True)


def load_and_format_data(input_file):
    """Loads the dataset, formats gender/category values, ensures numeric values, and filters valid data."""
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"❌ File not found: {input_file}. Please check the path and try again.")
        return None
    except Exception as e:
        print(f"❌ An error occurred while loading the file: {e}")
        return None

    if df.empty:
        print("\n❌ No data found in the CSV file. Exiting...")
        return None

    # ✅ Convert Gender & Product Category to Title Case
    df["Gender"] = df["Gender"].str.strip().str.title()
    df["Product Category"] = df["Product Category"].str.strip().str.title()

    # ✅ Remove invalid category values ("-")
    df = df[df["Product Category"] != "-"]

    # ✅ Ensure numeric values, replace NaN with 0
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce").fillna(0).astype(int)

    # ✅ Filter only 'Men' and 'Women'
    df = df[df["Gender"].isin(["Men", "Women"])]

    # ✅ Filter only `Last Year` data
    df = df[df["Year Type"] == "Last Year"]

    print("\n📊 **Step 1: Data Loaded & Formatted**")
    print(df.head(10))

    return df


def aggregate_and_pivot_data(df):
    """Aggregates values and pivots the dataset to have ISO Weeks as columns."""

    # ✅ Get last 8 weeks from last year in correct order (newest first, oldest last)
    last_8_weeks, _ = get_last_8_weeks_last_year()
    last_8_weeks_order = [
        (week["week_start"].year, week["week_start"].isocalendar()[1]) for week in reversed(last_8_weeks)
    ]

    print("\n📆 **Step 2: Expected Week Order (newest → oldest):**", last_8_weeks_order)

    # ✅ Ensure each (Gender, Category, ISO Week) has a single unique Value
    df_sorted = df.groupby(["ISO Week", "Gender", "Product Category"], as_index=False)["Value"].sum()

    print("\n📊 **Step 3: Aggregated Data Before Pivoting**")
    print(df_sorted.head(20))

    # ✅ Pivot table to have weeks as columns (newest → oldest)
    df_pivot = df_sorted.pivot_table(
        index=["Gender", "Product Category"], 
        columns="ISO Week", 
        values="Value", 
        aggfunc="sum"
    ).reset_index()

    # ✅ Reorder the week columns from newest to oldest
    iso_weeks_sorted = [week[1] for week in last_8_weeks_order]
    df_pivot = df_pivot[["Gender", "Product Category"] + iso_weeks_sorted]

    print("\n📊 **Step 4: Data After Pivoting**")
    print(df_pivot.head(10))

    # ✅ Replace NaN with 0 for missing values
    df_pivot = df_pivot.fillna(0)

    # ✅ Ensure correct 8-week average calculation (rounded to whole numbers)
    df_pivot["8-week avg"] = df_pivot[iso_weeks_sorted].mean(axis=1, numeric_only=True).round(0).astype(int)

    return df_pivot, iso_weeks_sorted


def sort_categories_by_latest_week(df_pivot, iso_weeks_sorted):
    """Sorts Men & Women categories in descending order based on the latest week's revenue."""

    latest_week_col = iso_weeks_sorted[-1] if iso_weeks_sorted else None

    men_df = df_pivot[df_pivot["Gender"] == "Men"]
    women_df = df_pivot[df_pivot["Gender"] == "Women"]

    if latest_week_col:
        men_df = men_df.sort_values(by=latest_week_col, ascending=False)
        women_df = women_df.sort_values(by=latest_week_col, ascending=False)
    else:
        print("\n⚠️ Could not find the latest week's column for sorting!")

    return men_df, women_df


def add_totals(men_df, women_df, iso_weeks_sorted):
    """Adds total and grand total rows for Men and Women categories."""
    
    def add_total_row(df, gender_label):
        """Summarizes total revenue for a gender and adds a row labeled 'Total'."""
        total_values = df[iso_weeks_sorted].sum()
        avg_value = total_values.mean(numeric_only=True)
        total_row = pd.DataFrame([[gender_label, "Total"] + total_values.tolist() + [avg_value]], 
                                columns=df.columns.tolist())
        return pd.concat([df, total_row], ignore_index=True)

    men_df = add_total_row(men_df, "Men")
    women_df = add_total_row(women_df, "Women")

    # ✅ **Combine both gender DataFrames**
    df_pivot = pd.concat([men_df, women_df], ignore_index=True)

    # ✅ **Add Grand Total Row**
    grand_total_values = df_pivot[df_pivot["Product Category"] == "Total"].drop(columns=["Gender", "Product Category", "8-week avg"]).sum()
    grand_total_avg = grand_total_values.mean(numeric_only=True)

    grand_total_row = pd.DataFrame([["Grand Total", ""] + grand_total_values.tolist() + [grand_total_avg]], 
                                   columns=df_pivot.columns)

    df_pivot = pd.concat([df_pivot, grand_total_row], ignore_index=True)

    return df_pivot


def save_to_csv(df_pivot, output_file):
    """Saves the final processed DataFrame to CSV."""
    # Convert all numeric columns to int to remove decimals
    numeric_columns = df_pivot.select_dtypes(include=['float64']).columns
    for col in numeric_columns:
        df_pivot[col] = df_pivot[col].astype(int)
    
    df_pivot.to_csv(output_file, index=False)
    print(f"\n✅ Successfully saved Last Year's Gender & Category Revenue data to CSV: {output_file}")


# ✅ Main function to run the entire process
def process_gender_category_ly_data():
    """Runs the full pipeline: Load → Aggregate → Sort → Add Totals → Save."""
    
    df = load_and_format_data(INPUT_FILE)
    if df is None:
        return

    df_pivot, iso_weeks_sorted = aggregate_and_pivot_data(df)

    men_df, women_df = sort_categories_by_latest_week(df_pivot, iso_weeks_sorted)

    df_final = add_totals(men_df, women_df, iso_weeks_sorted)

    print("\n📊 **Final Processed Data**")
    print(df_final.to_string(index=False))  # ✅ Print the full DataFrame

    save_to_csv(df_final, CSV_OUTPUT_FILE)


# ✅ Run the script
if __name__ == "__main__":
    process_gender_category_ly_data()