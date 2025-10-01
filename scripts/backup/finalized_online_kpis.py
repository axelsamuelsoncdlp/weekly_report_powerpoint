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
INPUT_FILE = os.path.join(BASE_DIR, "data", "raw", "online_kpis_raw.csv")
CSV_OUTPUT_FILE = os.path.join(BASE_DIR, "data", "final", "online_kpis_final.csv")

# ✅ Ensure output directory exists
os.makedirs(os.path.dirname(CSV_OUTPUT_FILE), exist_ok=True)

    # ✅ Apply strict formatting before pivoting
    def format_value(row):
        """Applies different rounding and scaling based on metric type."""
        if "Conversion Rate" in row["Metric"]:
            return round(row["Value"], 1)  # 1 decimal for Conversion Rate
        elif "COS" in row["Metric"]:
            return round(row["Value"], 0)  # 0 decimals for COS
        elif "Online Media Spend" in row["Metric"]:
            return round(row["Value"] / 1000, 0)  # Whole number in thousands
        elif "Sessions" in row["Metric"]:
            return round(row["Value"] / 1000, 1)  # 1 decimal in thousands
        else:
            return round(row["Value"], 0)  # 0 decimals for everything else


def sort_and_format_kpi_data(input_file, csv_output):
    """Sorts KPI data based on the last 8 weeks and reformats it with weeks as columns, with the most recent week on the left."""

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
    required_columns = {"Calendar Year", "ISO Week", "Metric", "Value", "Year Type"}
    if not required_columns.issubset(df.columns):
        print(f"❌ Missing required columns: {required_columns - set(df.columns)}")
        return

    # ✅ Convert 'Value' column to numeric early (handling potential string issues)
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    df["Value"] = df.apply(format_value, axis=1)

    # ✅ Get last 8 weeks in correct order (newest first, oldest last)
    last_8_weeks, _ = get_last_8_weeks()
    last_8_weeks_order = [
        (week["week_start"].year, week["week_start"].isocalendar()[1]) for week in reversed(last_8_weeks)
    ]

    # ✅ Assign sorting order based on the correct week order
    df["SortOrder"] = df.apply(
        lambda row: last_8_weeks_order.index((row["Calendar Year"], row["ISO Week"]))
        if (row["Calendar Year"], row["ISO Week"]) in last_8_weeks_order else float("inf"),
        axis=1
    )

    # ✅ Sort data based on the last 8 weeks order
    df_sorted = df.sort_values(by="SortOrder").drop(columns=["SortOrder"])

    # ✅ Pivot table to have weeks as columns (newest → oldest)
    df_pivot = df_sorted.pivot_table(
        index=["Metric", "Year Type"], 
        columns="ISO Week", 
        values="Value", 
        aggfunc="first"
    ).reset_index()

    # ✅ Reorder the week columns from newest to oldest
    iso_weeks_sorted = [week[1] for week in last_8_weeks_order]
    df_pivot = df_pivot[["Metric", "Year Type"] + iso_weeks_sorted]

    # ✅ Convert non-decimal metrics to integers after pivoting
    for col in iso_weeks_sorted:
        if col in df_pivot.columns:
            df_pivot[col] = df_pivot.apply(
                lambda row: int(row[col]) if pd.notna(row[col]) and row["Metric"] not in ["COS%", "Conversion Rate (%)"]
                else row[col],
                axis=1
            )

    # ✅ Display full DataFrame in terminal
    pd.set_option("display.max_rows", None)
    pd.set_option("display.float_format", "{:.2f}".format)

    print("\n📊 **Formatted KPI Data:**")
    print(df_pivot.to_string(index=False))  # Display full DataFrame in readable format

    # ✅ Save the sorted and formatted data as a CSV file
    df_pivot.to_csv(csv_output, index=False)

    print(f"\n✅ Successfully saved formatted KPI data to CSV: {csv_output}")


# ✅ Run the script
if __name__ == "__main__":
    sort_and_format_kpi_data(INPUT_FILE, CSV_OUTPUT_FILE)