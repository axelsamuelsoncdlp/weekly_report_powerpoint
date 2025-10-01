import sys
import os
import pandas as pd

# === Setup import paths ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from calculator.metrics_calculator import load_data

# === Load and prepare data ===
df = load_data()
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df[df['Date'].notna()]
df['Year'] = df['Date'].dt.year

# === Define YTD window ===
start_date = "01-01"
end_date = "05-22"
df['MM-DD'] = df['Date'].dt.strftime("%m-%d")
df_ytd = df[df['MM-DD'].between(start_date, end_date)]

# === Group and aggregate ===
ytd_summary = (
    df_ytd.groupby(['Year', 'Category'])['Gross Revenue (ex. VAT)']
    .sum()
    .reset_index()
    .pivot(index='Category', columns='Year', values='Gross Revenue (ex. VAT)')
    .fillna(0)
)

# === Calculate YoY Growth ===
if 2024 in ytd_summary.columns and 2025 in ytd_summary.columns:
    ytd_summary['YoY Growth % (2025 vs 2024)'] = ((ytd_summary[2025] - ytd_summary[2024]) / ytd_summary[2024]) * 100
else:
    ytd_summary['YoY Growth % (2025 vs 2024)'] = None

# === Format ===
ytd_summary = ytd_summary.reset_index().sort_values(by='YoY Growth % (2025 vs 2024)', ascending=False)

# === Display ===
import ace_tools as tools; tools.display_dataframe_to_user(name="YTD Growth by Product Category", dataframe=ytd_summary)
