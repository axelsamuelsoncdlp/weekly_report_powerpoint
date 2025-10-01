import sys
import os
import pandas as pd

# === Setup import paths ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.metrics_calculator import load_data

# === Step 1: Load and clean data ===
df = load_data()
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Customer E-mail'] = df['Customer E-mail'].str.lower().str.strip()
df = df[df['Date'].notna()]

# === Step 2: Filter to Online Swimwear Orders ===
swimwear_df = df[
    (df["Channel Group"] == "Online") &
    (df["Category"].fillna("").str.upper() == "SWIMWEAR") &
    (df["Customer E-mail"] != "-")
].copy()

swimwear_df['Year'] = swimwear_df['Date'].dt.year

# === Step 3: Get first swimwear order date per customer ===
first_swimwear = swimwear_df.groupby('Customer E-mail')['Date'].min().reset_index()
first_swimwear.columns = ['Customer E-mail', 'First Swimwear Order Date']
first_swimwear['First Swimwear Year'] = first_swimwear['First Swimwear Order Date'].dt.year

# === Step 4: Get first-ever purchase date per customer (from full dataset) ===
first_overall = df.groupby('Customer E-mail')['Date'].min().reset_index()
first_overall.columns = ['Customer E-mail', 'First Ever Order Date']

# === Step 5: Merge into swimwear_df ===
swimwear_df = swimwear_df.merge(first_swimwear, on='Customer E-mail', how='left')
swimwear_df = swimwear_df.merge(first_overall, on='Customer E-mail', how='left')

# === Step 6: Classify customer swim type based on 'New/Returning Customer' and year ===
def classify_customer(row):
    if row['New/Returning Customer'] == 'New' and row['Year'] == row['First Swimwear Year']:
        return 'New Customer / New Swim'
    elif row['New/Returning Customer'] == 'Returning' and row['Year'] == row['First Swimwear Year']:
        return 'Returning Customer / New Swim'
    else:
        return 'Returning Customer / Returning Swim'

swimwear_df['Customer Swim Type'] = swimwear_df.apply(classify_customer, axis=1)

# === Step 6b: Calculate Swimwear LTV and apply only to last swimwear order per customer ===
ltv = swimwear_df.groupby('Customer E-mail')['Gross Revenue (ex. VAT)'].sum().reset_index()
ltv.columns = ['Customer E-mail', 'Swimwear LTV (ex. VAT)']

# Identify latest swimwear order row per customer
latest_order_idx = swimwear_df.groupby('Customer E-mail')['Date'].idxmax()

# Create empty column
swimwear_df['Swimwear LTV (ex. VAT)'] = pd.NA

# Extract last rows and merge with LTV
last_orders = swimwear_df.loc[latest_order_idx][['Customer E-mail', 'Date']].merge(
    ltv, on='Customer E-mail', how='left'
)

# Assign LTV only to last row per customer
for _, row in last_orders.iterrows():
    swimwear_df.loc[
        (swimwear_df['Customer E-mail'] == row['Customer E-mail']) &
        (swimwear_df['Date'] == row['Date']),
        'Swimwear LTV (ex. VAT)'
    ] = row['Swimwear LTV (ex. VAT)']

# === Step 6c: Debug print for specific order ===
debug_order_id = "SHP100233629"
debug_rows = swimwear_df[swimwear_df['Order Id'] == debug_order_id]

print(f"\n🔍 Debug – Order Id: {debug_order_id}")
if not debug_rows.empty:
    print(debug_rows[['Date', 'Customer E-mail', 'Order Id', 'Product', 'First Ever Order Date', 'First Swimwear Order Date', 'New/Returning Customer', 'Customer Swim Type', 'Swimwear LTV (ex. VAT)']])
else:
    print("⚠️ No rows found for this Order Id.")

# === Step 7: Summary output ===
summary = swimwear_df.groupby(['Year', 'Customer Swim Type'])['Customer E-mail'].nunique().reset_index()
pivot_summary = summary.pivot(index='Year', columns='Customer Swim Type', values='Customer E-mail').fillna(0).astype(int).reset_index()

print("✅ Swimwear Orders Extracted")
print("🔢 Total rows:", len(swimwear_df))
print("👥 Unique customers:", swimwear_df['Customer E-mail'].nunique())
print("\n📊 Summary – Swimwear Customer Types per Year:")
print(pivot_summary)

# === Step 8: Save cleaned data with classifications ===
output_path = "/Users/axelsamuelson/Documents/CDLP_code/weekly_reports/data/analyse/swimwear_orders_cleaned.csv"
swimwear_df.to_csv(output_path, index=False)
print(f"\n📦 Saved cleaned swimwear orders with classifications to: {output_path}")
