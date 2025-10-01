import os
import pandas as pd

# ✅ Define paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INPUT_FILE = os.path.join(BASE_DIR, "data", "raw", "gender_category_share_raw.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "final", "gender_category_share_final.csv")

# ✅ Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# ✅ Load dataset
df = pd.read_csv(INPUT_FILE)

# ✅ Pivot the dataset to match the required format
df_pivot = df.pivot_table(
    index=["Gender", "Product Category"],  # "ISO Week" becomes column headers
    columns="ISO Week",
    values="Share (%)",
    aggfunc="sum"
).reset_index()

# ✅ Rename columns
df_pivot.rename(columns={"Product Category": "Product Category"}, inplace=True)

# ✅ Get list of ISO week columns & sort them correctly (51, 52, 1, 2, 3, 4, 5, 6)
week_columns = [col for col in df_pivot.columns if isinstance(col, (int, float))]
sorted_weeks = sorted(week_columns, key=lambda x: (x < 10, x))  # Ensures 51, 52 appear first

# ✅ Determine the most recent week for sorting (Week 6 in this case)
latest_week = 6 if 6 in sorted_weeks else max(sorted_weeks)  # Default to latest available week

# ✅ Convert latest week column to numeric for sorting **before formatting**
df_pivot["Sort Value"] = df_pivot[latest_week].fillna(0)

# ✅ Sort by latest week's share within each Gender separately
df_pivot = df_pivot.sort_values(by=["Gender", "Sort Value"], ascending=[True, False]).drop(columns=["Sort Value"])

# ✅ Calculate 8-week average share column **before formatting**
df_pivot["8-Week Avg"] = df_pivot[sorted_weeks].mean(axis=1).round(0)

# ✅ Reorder the dataframe with the correct columns
df_pivot = df_pivot[["Gender", "Product Category"] + sorted_weeks + ["8-Week Avg"]]

# ✅ Formatting function: No decimals, negatives in parentheses, and replace 0 with "-"
def format_share(value):
    try:
        value = int(round(float(value)))  # Convert to integer
        if value == 0:
            return "-"
        elif value < 0:
            return f"({abs(value)})"
        else:
            return str(value)
    except (ValueError, TypeError):
        return "-"

# ✅ Apply formatting **AFTER sorting**
for col in sorted_weeks + ["8-Week Avg"]:
    df_pivot[col] = df_pivot[col].astype(str).map(format_share)

# ✅ Create a new dataframe for storing results with total rows placed correctly
final_list = []

# ✅ Process each gender separately to insert total rows correctly
for gender in ["Men", "Women"]:
    # Get categories (exclude Total row)
    gender_df = df_pivot[(df_pivot["Gender"] == gender) & (df_pivot["Product Category"] != "Total")]

    # ✅ Append the gender-specific sorted categories
    final_list.append(gender_df)

    # ✅ Get the Total row for this gender from the original data
    total_row = df_pivot[(df_pivot["Gender"] == gender) & (df_pivot["Product Category"] == "Total")]

    # ✅ Append the total row **directly below the last category for the gender**
    if not total_row.empty:
        final_list.append(total_row)

# ✅ Concatenate the final ordered dataframe
df_final = pd.concat(final_list, ignore_index=True)

# ✅ Calculate the Grand Total row (should always be 100% for each week)
grand_total_values = ["100%"] * len(sorted_weeks) + ["100%"]  # 100% for each week and 8-week avg

grand_total_row = pd.DataFrame([["", "Grand Total"] + grand_total_values], columns=df_final.columns)

# ✅ Append Grand Total row
df_final = pd.concat([df_final, grand_total_row], ignore_index=True)

# ✅ Save the formatted data **WITHOUT index column**
df_final.to_csv(OUTPUT_FILE, index=False)

# ✅ Print confirmation
print(f"\n✅ Finalized gender-category share data successfully saved to: {OUTPUT_FILE}")

# ✅ Preview the first few rows WITHOUT index
print("\n📊 **Preview of Finalized Data:**")
print(df_final.to_string(index=False))
