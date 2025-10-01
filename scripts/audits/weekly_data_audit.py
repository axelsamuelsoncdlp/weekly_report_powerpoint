import os
import pandas as pd

# Define file path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATA_PATH = os.path.join(BASE_DIR, "data", "formatted", "weekly_data_formatted.csv")

# Check if the file exists
if os.path.exists(DATA_PATH):
    # Load the CSV file
    df = pd.read_csv(DATA_PATH, low_memory=False)
    
    # Print all column names
    print("\n✅ **Column Names in weekly_data_formatted.csv:**")
    for col in df.columns:
        print(f"- {col}")
    
    # Print first few rows for verification
    print("\n📊 **First 5 Rows of Data:**")
    print(df.head().to_string(index=False))
else:
    print(f"❌ File not found: {DATA_PATH}")
