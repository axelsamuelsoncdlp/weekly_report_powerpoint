import os
import pandas as pd

# Define file path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATA_PATH = os.path.join(BASE_DIR, "data", "formatted", "weekly_data_formatted.csv")

# Check if the file exists
if os.path.exists(DATA_PATH):
    # Load the CSV file
    df = pd.read_csv(DATA_PATH, low_memory=False)
    
    # Check if "Channel Group" column exists
    if "Channel Group" in df.columns:
        unique_values = df["Channel Group"].dropna().unique()
        print("\n✅ **Unique Values in 'Channel Group' Column:**")
        for value in unique_values:
            print(f"- {value}")
    else:
        print("❌ Column 'Channel Group' not found in the dataset!")
else:
    print(f"❌ File not found: {DATA_PATH}")
