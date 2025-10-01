import sys
import os
import pandas as pd

# ✅ Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Define file paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CURRENT_YEAR_FILE = os.path.join(BASE_DIR, "data", "final", "gender_category_final.csv")
LAST_YEAR_FILE = os.path.join(BASE_DIR, "data", "final", "gender_category_ly_final.csv")
CSV_OUTPUT_FILE = os.path.join(BASE_DIR, "data", "final", "gender_category_growth_final.csv")

# ✅ Ensure output directory exists
os.makedirs(os.path.dirname(CSV_OUTPUT_FILE), exist_ok=True)


def load_and_prepare_data():
    """Loads and ensures all categories are included for both current and last year."""
    try:
        df_current = pd.read_csv(CURRENT_YEAR_FILE)
        df_last_year = pd.read_csv(LAST_YEAR_FILE)
    except FileNotFoundError as e:
        print(f"❌ File not found: {e.filename}")
        return None, None, None
    except Exception as e:
        print(f"❌ An error occurred while loading the files: {e}")
        return None, None, None

    # ✅ Identify numeric week columns (ISO week numbers)
    week_columns = [col for col in df_current.columns if col.isdigit()]

    # ✅ Ensure required columns exist
    required_columns = set(week_columns + ["8-week avg", "Gender", "Product Category"])
    if not required_columns.issubset(df_current.columns) or not required_columns.issubset(df_last_year.columns):
        print(f"❌ Missing required columns in one of the files: {required_columns}")
        return None, None, None

    # ✅ Create a full list of unique Gender-Product Category combinations
    all_categories = pd.concat([df_current[['Gender', 'Product Category']], df_last_year[['Gender', 'Product Category']]]).drop_duplicates()

    # ✅ Merge to ensure all categories exist
    df_current = all_categories.merge(df_current, on=["Gender", "Product Category"], how="left")
    df_last_year = all_categories.merge(df_last_year, on=["Gender", "Product Category"], how="left")

    # ✅ Fill missing values with 0 or NaN (depending on preference)
    df_current.fillna(0, inplace=True)
    df_last_year.fillna(0, inplace=True)

    print("\n📊 **Step 1: Loaded Data with All Categories**")
    print(f"Current Year Data: {df_current.shape}, Last Year Data: {df_last_year.shape}")

    return df_current, df_last_year, week_columns

def calculate_growth(df_current, df_last_year, week_columns):
    """Calculates the percentage growth based on last year's values."""

    # ✅ Ensure both dataframes have the same column names before merging
    rename_dict_current = {col: f"{col}_current" for col in week_columns + ["8-week avg"]}
    rename_dict_last_year = {col: f"{col}_ly" for col in week_columns + ["8-week avg"]}

    df_current = df_current.rename(columns=rename_dict_current)
    df_last_year = df_last_year.rename(columns=rename_dict_last_year)

    # ✅ Merge both datasets to align structures (preserve Gender & Category from df_current)
    df_growth = df_current.merge(
        df_last_year,
        left_index=True,  # Ensure we merge correctly
        right_index=True,
        how="left"
    )

    # ✅ Restore Gender & Product Category
    df_growth["Gender"] = df_current["Gender"]
    df_growth["Product Category"] = df_current["Product Category"]

    # ✅ Calculate Year-over-Year Growth for each week
    for week in week_columns:
        current_col = f"{week}_current"
        last_year_col = f"{week}_ly"

        if current_col in df_growth.columns and last_year_col in df_growth.columns:
            df_growth[week] = ((df_growth[current_col] - df_growth[last_year_col]) / df_growth[last_year_col]) * 100
            df_growth[week] = df_growth[week].replace([float("inf"), -float("inf")], None)  # Handle division by zero

    # ✅ Calculate 8-week average growth from individual week growths
    df_growth["8-week avg"] = df_growth[week_columns].mean(axis=1)

    # ✅ Keep only relevant columns (Gender, Product Category, Growth Values)
    growth_columns = ["Gender", "Product Category"] + week_columns + ["8-week avg"]
    df_growth = df_growth[growth_columns]

    print("\n📊 **Step 2: Calculated Year-over-Year Growth (With Gender & Category)**")
    print(df_growth.to_string(index=False))

    return df_growth


def save_to_csv(df_growth, output_file):
    """Saves the final processed Growth DataFrame to CSV."""
    # Convert all numeric columns to remove decimals
    numeric_columns = df_growth.select_dtypes(include=['float64']).columns
    for col in numeric_columns:
        # Round to 0 decimal places and format as integers
        df_growth[col] = df_growth[col].round(0)
        # Convert to string with integer formatting, handling NaN values
        df_growth[col] = df_growth[col].apply(lambda x: f"{int(x)}" if pd.notna(x) else "")
    
    df_growth.to_csv(output_file, index=False)
    print(f"\n✅ Successfully saved Gender & Category Growth data to CSV: {output_file}")


def process_gender_category_growth():
    """Runs the full pipeline: Load → Calculate Growth → Print → Save."""

    # ✅ Load and prepare the data
    df_current, df_last_year, week_columns = load_and_prepare_data()
    if df_current is None or df_last_year is None:
        print("❌ No data available for processing. Exiting...")
        return

    # ✅ Calculate Year-over-Year Growth
    df_growth = calculate_growth(df_current, df_last_year, week_columns)

    # ✅ Drop Gender & Category Columns
    df_growth_no_labels = df_growth.drop(columns=["Gender", "Category"], errors="ignore")

    # ✅ Print DataFrame without Gender & Category
    print("\n📊 **Step 3: Final Growth Data (Without Gender & Category)**")
    print(df_growth_no_labels.to_string(index=False))

    # ✅ Save final output
    save_to_csv(df_growth_no_labels, CSV_OUTPUT_FILE)


# ✅ Run the script
if __name__ == "__main__":
    process_gender_category_growth()