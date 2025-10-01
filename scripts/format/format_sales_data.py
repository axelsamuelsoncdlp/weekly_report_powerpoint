import os
import pandas as pd

# ✅ Define file paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATA_FOLDER = os.path.join(BASE_DIR, "data")
FORMATTED_FOLDER = os.path.join(DATA_FOLDER, "formatted")
EXCEL_INPUT_FILE = os.path.join(DATA_FOLDER, "Weekly_Data.xlsx")
CSV_OUTPUT_FILE = os.path.join(FORMATTED_FOLDER, "weekly_data_formatted.csv")

# ✅ Ensure output directories exist
os.makedirs(FORMATTED_FOLDER, exist_ok=True)

def convert_weekly_data():
    """Loads Weekly_Data.xlsx, formats it, and saves it as weekly_data_formatted.csv."""
    if not os.path.exists(EXCEL_INPUT_FILE):
        print(f"❌ Missing file: {EXCEL_INPUT_FILE}. Please ensure the file exists in the data folder.")
        return

    print("📥 Loading Weekly_Data.xlsx...")
    df = pd.read_excel(EXCEL_INPUT_FILE, engine="openpyxl")

    # ✅ Convert dates and clean column names
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

    # ✅ Save formatted CSV
    df.to_csv(CSV_OUTPUT_FILE, index=False)
    print(f"✅ Formatted data saved to: {CSV_OUTPUT_FILE}")

if __name__ == "__main__":
    convert_weekly_data()
