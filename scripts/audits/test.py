import pandas as pd
import os
from calculator.date_utils import get_latest_full_week  # Import function
from calculator.metrics_calculator import load_spend_data  # Load marketing spend

# ✅ Define file paths
BASE_DIR = "/Users/axelsamuelson/Documents/CDLP_code/weekly_reports/data"
CSV_FILE_PATH = os.path.join(BASE_DIR, "formatted", "weekly_data_formatted.csv")
SPEND_FILE_PATH = os.path.join(BASE_DIR, "formatted", "marketing_spend_formatted.csv")

# ✅ Load CSV files
csv_df = pd.read_csv(CSV_FILE_PATH, low_memory=False)
spend_df = load_spend_data()

# ✅ Convert 'Date' to datetime format
csv_df["Date"] = pd.to_datetime(csv_df["Date"], errors="coerce").dt.date

# ✅ Get the latest week's date range
latest_week_values = get_latest_full_week()

if isinstance(latest_week_values, dict) and "current_week" in latest_week_values:
    current_week_start, current_week_end = latest_week_values["current_week"]
else:
    raise ValueError("❌ Unexpected output from `get_latest_full_week()`. Expected a dictionary with 'current_week' key.")

# ✅ Filter data for the current week
current_week_data = csv_df[(csv_df["Date"] >= current_week_start) & (csv_df["Date"] <= current_week_end)]

# ✅ Separate Online and Retail data
online_data = current_week_data[current_week_data["Channel Group"] == "Online"]
retail_data = current_week_data[current_week_data["Channel Group"] == "Retail"]

# ✅ Sum Online & Retail Gross Revenue (ex. VAT & inc. VAT)
online_gross_revenue_ex_vat = online_data["Gross Revenue (ex. VAT)"].sum()
online_gross_revenue_inc_vat = online_data["Gross Revenue (inc. VAT)"].sum()
retail_gross_revenue_ex_vat = retail_data["Gross Revenue (ex. VAT)"].sum()
retail_gross_revenue_inc_vat = retail_data["Gross Revenue (inc. VAT)"].sum()

# ✅ Filter New and Returning Customers for Online
new_customers_data = online_data[online_data["New/Returning Customer"] == "New"]
returning_customers_data = online_data[online_data["New/Returning Customer"] == "Returning"]

# ✅ Sum Gross Revenue (ex. VAT & inc. VAT) for New and Returning Customers (Online)
gross_revenue_ex_vat_new = new_customers_data["Gross Revenue (ex. VAT)"].sum()
gross_revenue_ex_vat_returning = returning_customers_data["Gross Revenue (ex. VAT)"].sum()
gross_revenue_inc_vat_new = new_customers_data["Gross Revenue (inc. VAT)"].sum()
gross_revenue_inc_vat_returning = returning_customers_data["Gross Revenue (inc. VAT)"].sum()

# ✅ Count rows:
num_rows_with_gross_revenue = online_data[online_data["Gross Revenue (ex. VAT)"] > 0].shape[0]
num_rows_with_new_or_returning = online_data[online_data["New/Returning Customer"].notna()].shape[0]
num_rows_with_both = online_data[
    (online_data["Gross Revenue (ex. VAT)"] > 0) & 
    (online_data["New/Returning Customer"].notna())
].shape[0]

# ✅ Count unique orders for Online & Retail
unique_orders_total_online = online_data["Order Id"].nunique()
unique_orders_total_retail = retail_data["Order Id"].nunique()
unique_orders_new = new_customers_data["Order Id"].nunique()
unique_orders_returning = returning_customers_data["Order Id"].nunique()

# ✅ Calculate AOV (Average Order Value) for New and Returning Customers (ex. VAT & inc. VAT)
aov_ex_vat_new_customers = (gross_revenue_ex_vat_new / unique_orders_new) if unique_orders_new > 0 else 0
aov_ex_vat_returning_customers = (gross_revenue_ex_vat_returning / unique_orders_returning) if unique_orders_returning > 0 else 0

aov_inc_vat_new_customers = (gross_revenue_inc_vat_new / unique_orders_new) if unique_orders_new > 0 else 0
aov_inc_vat_returning_customers = (gross_revenue_inc_vat_returning / unique_orders_returning) if unique_orders_returning > 0 else 0

# ✅ Filter and sum Marketing Spend
if spend_df is not None:
    spend_df["Date"] = pd.to_datetime(spend_df["Date"], errors="coerce").dt.date
    current_week_spend = spend_df[
        (spend_df["Date"] >= current_week_start) & (spend_df["Date"] <= current_week_end)
    ]["Total Spend"].sum()
else:
    current_week_spend = 0

# ✅ Calculate nCAC (New Customer Acquisition Cost)
ncac = (current_week_spend / unique_orders_new) if unique_orders_new > 0 else 0

# ✅ Print results
print("\n📆 **Gross Revenue for Current Full Week**")
print(f"🗓️ Period: {current_week_start} to {current_week_end}")
print(f"💰 Total Online Gross Revenue (ex. VAT): {online_gross_revenue_ex_vat:,.2f} SEK")
print(f"💰 Total Online Gross Revenue (inc. VAT): {online_gross_revenue_inc_vat:,.2f} SEK")
print(f"🏬 Total Retail Gross Revenue (ex. VAT): {retail_gross_revenue_ex_vat:,.2f} SEK")
print(f"🏬 Total Retail Gross Revenue (inc. VAT): {retail_gross_revenue_inc_vat:,.2f} SEK")

print("\n📊 **Gross Revenue Breakdown by Customer Type (Online Only)**")
print(f"🆕 New Customers Gross Revenue (ex. VAT): {gross_revenue_ex_vat_new:,.2f} SEK")
print(f"🆕 New Customers Gross Revenue (inc. VAT): {gross_revenue_inc_vat_new:,.2f} SEK")
print(f"🔄 Returning Customers Gross Revenue (ex. VAT): {gross_revenue_ex_vat_returning:,.2f} SEK")
print(f"🔄 Returning Customers Gross Revenue (inc. VAT): {gross_revenue_inc_vat_returning:,.2f} SEK")

print("\n📊 **Row Counts**")
print(f"📝 Rows with Gross Revenue (ex. VAT): {num_rows_with_gross_revenue:,}")
print(f"👥 Rows with New/Returning Customer: {num_rows_with_new_or_returning:,}")
print(f"✅ Rows with BOTH Gross Revenue & New/Returning Customer: {num_rows_with_both:,}")

print("\n📊 **Unique Orders Count**")
print(f"📦 Unique Orders (Online): {unique_orders_total_online:,}")
print(f"🏬 Unique Orders (Retail): {unique_orders_total_retail:,}")
print(f"🆕 Unique Orders (New Customers - Online): {unique_orders_new:,}")
print(f"🔄 Unique Orders (Returning Customers - Online): {unique_orders_returning:,}")

print("\n📊 **AOV (Average Order Value) Based on Gross Revenue (ex. VAT)**")
print(f"🆕 AOV New Customers (ex. VAT): {aov_ex_vat_new_customers:,.2f} SEK")
print(f"🔄 AOV Returning Customers (ex. VAT): {aov_ex_vat_returning_customers:,.2f} SEK")

print("\n📊 **AOV (Average Order Value) Based on Gross Revenue (inc. VAT)**")
print(f"🆕 AOV New Customers (inc. VAT): {aov_inc_vat_new_customers:,.2f} SEK")
print(f"🔄 AOV Returning Customers (inc. VAT): {aov_inc_vat_returning_customers:,.2f} SEK")

print("\n📊 **Marketing Spend & New Customer Acquisition Cost**")
print(f"📢 Marketing Spend (Current Week): {current_week_spend:,.2f} SEK")
print(f"💳 New Customer Acquisition Cost (nCAC): {ncac:,.2f} SEK")
