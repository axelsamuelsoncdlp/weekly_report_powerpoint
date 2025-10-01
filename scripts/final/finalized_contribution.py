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
INPUT_FILE = os.path.join(BASE_DIR, "data", "raw", "contribution_raw.csv")
CSV_OUTPUT_FILE = os.path.join(BASE_DIR, "data", "final", "contribution_final.csv")

# ✅ Ensure output directory exists
os.makedirs(os.path.dirname(CSV_OUTPUT_FILE), exist_ok=True)


def format_kpi_data(df):
    """
    Formats KPI data with specific decimal handling:
    - Conversion Rate (%) → 1 decimal
    - COS% → 0 decimals
    - All other values → 0 decimals (No division by 1000 anymore!)
    """

    print("\n🔍 **Step 1: Raw 'Value' Column Before Formatting**")
    print(df[["Metric", "Customer Type", "Value"]].head(10))  # Inspect raw values

    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")  # Ensure numeric values

    def apply_formatting(row):
        """Applies specific rounding rules based on metric type."""
        original_value = row["Value"]  # Keep original for logging

        if "Conversion Rate" in row["Metric"]:
            formatted_value = round(row["Value"], 1)  # 1 decimal for Conversion Rate
        elif "COS" in row["Metric"]:
            formatted_value = round(row["Value"], 0)  # 0 decimals for COS
        else:
            formatted_value = round(row["Value"], 0)  # 0 decimals for everything else

        # Log transformation for debugging
        print(f"🔄 Formatting '{row['Metric']} ({row['Customer Type']})': {original_value} → {formatted_value}")
        return formatted_value

    df["Value"] = df.apply(apply_formatting, axis=1)

    print("\n🔍 **Step 2: 'Value' Column After Formatting**")
    print(df[["Metric", "Customer Type", "Value"]].head(10))  # Inspect transformed values

    return df


def sort_and_save_kpi_data(input_file, csv_output):
    """Loads KPI data, sorts it based on the last 8 weeks, formats it, and saves as CSV."""

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
    required_columns = {"Calendar Year", "ISO Week", "Metric", "Customer Type", "Value", "Year Type"}
    if not required_columns.issubset(df.columns):
        print(f"❌ Missing required columns: {required_columns - set(df.columns)}")
        return

    print("\n📊 **Step 0: Raw Data Loaded**")
    print(df.head(10))

    # ✅ Apply formatting BEFORE pivoting
    df = format_kpi_data(df)

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

    print("\n📊 **Step 4: Sorted KPI Data Before Pivoting**")
    print(df_sorted.head(10))

    # ✅ Pivot table to have weeks as columns (newest → oldest)
    df_pivot = df_sorted.pivot_table(
        index=["Metric", "Customer Type", "Year Type"], 
        columns="ISO Week", 
        values="Value", 
        aggfunc="first"
    ).reset_index()

    # ✅ Reorder the week columns from newest to oldest
    iso_weeks_sorted = [week[1] for week in last_8_weeks_order]
    df_pivot = df_pivot[["Metric", "Customer Type", "Year Type"] + iso_weeks_sorted]

    print("\n📊 **Step 5: KPI Data After Pivoting**")
    print(df_pivot.head(10))

    # ✅ Force final formatting after pivoting (No conversion to thousands!)
    for col in iso_weeks_sorted:
        if col in df_pivot.columns:
            df_pivot[col] = df_pivot.apply(
                lambda row: int(row[col]) if pd.notna(row[col]) and row["Metric"] not in ["COS%", "Conversion Rate (%)"]
                else row[col],
                axis=1
            )

    print("\n📊 **Step 6: KPI Data After Final Formatting**")
    print(df_pivot.head(10))

    # ✅ Display full DataFrame in terminal
    pd.set_option("display.max_rows", None)
    pd.set_option("display.float_format", lambda x: f"{x:.1f}" if isinstance(x, float) else str(int(x)))

    print("\n📊 **Final Formatted KPI Data:**")
    print(df_pivot.to_string(index=False))  # Display full DataFrame in readable format

    # ✅ Save the sorted and formatted data as a CSV file
    df_pivot.to_csv(csv_output, index=False)

    print(f"\n✅ Successfully saved formatted KPI data to CSV: {csv_output}")


# ✅ Run the script
if __name__ == "__main__":
    sort_and_save_kpi_data(INPUT_FILE, CSV_OUTPUT_FILE)
