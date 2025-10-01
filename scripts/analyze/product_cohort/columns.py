import pandas as pd

# Load the Excel file
file_path = "/Users/axelsamuelson/Documents/CDLP_code/weekly_reports/data/weekly_data.xlsx"
df = pd.read_excel(file_path)

# Print each column name
print("📋 Column names:")
print(df.columns.tolist())
