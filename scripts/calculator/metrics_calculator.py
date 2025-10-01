import sys
import os
import pandas as pd

# Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.date_utils import get_latest_full_week
from calculator.orders import deduplicate_orders  # ✅ Importing correct order calculation

# ✅ Get absolute path dynamically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "formatted", "weekly_data_formatted.csv")
SPEND_DATA_PATH = os.path.join(BASE_DIR, "data", "formatted", "marketing_spend_formatted.csv")

def load_data():
    """Loads revenue and marketing spend data."""
    df = pd.read_csv(DATA_PATH, low_memory=False)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
    return df

def load_spend_data():
    """Loads formatted marketing spend data."""
    if os.path.exists(SPEND_DATA_PATH):
        spend_df = pd.read_csv(SPEND_DATA_PATH, low_memory=False)
        spend_df["Date"] = pd.to_datetime(spend_df["Date"], errors="coerce").dt.date
        return spend_df
    else:
        print("⚠️ Marketing Spend file not found. Using zero values.")
        return None

def load_session_data():
    """Load session data from session_data.csv file."""
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    session_file = os.path.join(BASE_DIR, "data", "session_data.csv")
    
    if not os.path.exists(session_file):
        print(f"⚠️ Warning: Session data file not found: {session_file}")
        return pd.DataFrame()
    
    try:
        # Read CSV with comma separator (new format)
        df = pd.read_csv(session_file)
        
        # Rename columns to match expected format
        df = df.rename(columns={
            'Day': 'Date',
            'Sessions': 'Sessions'
        })
        
        # Convert Date column to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        # No need to aggregate since data is already aggregated by date
        return df
    except Exception as e:
        print(f"⚠️ Warning: Could not read session data: {e}")
        return pd.DataFrame()

def calculate_revenue_metrics(df, start_date, end_date):
    """Calculates revenue metrics, ensuring correct channel breakdown."""
    
    # ✅ Filter dataset for the given date range
    filtered_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

    # ✅ Group revenue by Channel (Ensuring exact matches)
    online_df = filtered_df[filtered_df["Sales Channel"] == "Online"]
    retail_df = filtered_df[filtered_df["Sales Channel"] == "Retail"]
    retail_popup_df = filtered_df[filtered_df["Sales Channel"] == "Retail Pop-up"]
    wholesale_df = filtered_df[filtered_df["Sales Channel"] == "Wholesale"]

    # ✅ Online Revenue Calculations
    gross_revenue_ex_vat = online_df["Gross Revenue"].sum()
    net_revenue = gross_revenue_ex_vat - online_df["Returns"].sum()

    # ✅ Returns & Return Rate
    online_returns = online_df["Returns"].sum()
    return_rate = round((online_returns / gross_revenue_ex_vat) * 100, 1) if gross_revenue_ex_vat > 0 else 0

    # ✅ Customer Metrics (Online Only)
    online_customers_df = online_df.dropna(subset=["Customer E-mail"])
    new_customers_df = online_customers_df[online_customers_df["New/Returning Customer"] == "New"]
    returning_customers_df = online_customers_df[online_customers_df["New/Returning Customer"] == "Returning"]

    new_customers = new_customers_df["Customer E-mail"].nunique()
    returning_customers = returning_customers_df["Customer E-mail"].nunique()

    # ✅ Sessions from session_data.csv
    session_df = load_session_data()
    if not session_df.empty:
        # Convert start_date and end_date to datetime for comparison
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date)
        session_filtered = session_df[(session_df["Date"] >= start_datetime) & (session_df["Date"] <= end_datetime)]
        total_sessions = session_filtered["Sessions"].sum()
    else:
        # Fallback to 0 if no session data
        total_sessions = 0
    total_online_orders = online_df["Order No"].nunique()

    # ✅ Conversion Rate (Only Online Orders)
    conversion_rate = (total_online_orders / total_sessions) * 100 if total_sessions > 0 else 0

    # ✅ Gross Revenue (ex. VAT) for New & Returning Customers
    gross_revenue_ex_vat_new = new_customers_df["Gross Revenue"].sum()
    gross_revenue_ex_vat_returning = returning_customers_df["Gross Revenue"].sum()

    # ✅ AOV Calculation (Now based on Gross Revenue ex VAT)
    aov_new_customers_ex_vat = (gross_revenue_ex_vat_new / new_customers) if new_customers > 0 else 0
    aov_returning_customers_ex_vat = (gross_revenue_ex_vat_returning / returning_customers) if returning_customers > 0 else 0

    # ✅ Retail & Wholesale Revenues (Corrected)
    retail_concept_store_revenue = retail_df["Gross Revenue"].sum()  # ✅ Exact "Retail" match
    retail_popups_revenue = retail_popup_df["Gross Revenue"].sum()  # ✅ Exact "Retail Pop-up" match
    wholesale_revenue = wholesale_df["Gross Revenue"].sum()  # ✅ Exact "Wholesale" match

    # ✅ Total Retail Revenue (Summing Retail + Retail Pop-ups)
    retail_net_revenue = retail_concept_store_revenue + retail_popups_revenue

    return {
        "Gross Revenue": gross_revenue_ex_vat,
        "Net Revenue": net_revenue,
        "Returns": online_returns,
        "Return Rate": return_rate,
        "New Customers": new_customers,
        "Returning Customers": returning_customers,
        "Sessions": total_sessions,
        "Orders (Online Only)": total_online_orders,
        "Conversion Rate (%)": round(conversion_rate, 2),
        "Gross Revenue (ex. VAT) - New Customers": gross_revenue_ex_vat_new,
        "Gross Revenue (ex. VAT) - Returning Customers": gross_revenue_ex_vat_returning,
        "AOV New Customers (ex. VAT)": round(aov_new_customers_ex_vat, 2),
        "AOV Returning Customers (ex. VAT)": round(aov_returning_customers_ex_vat, 2),
        "Retail Concept Store Revenue": retail_concept_store_revenue,
        "Retail Pop-ups Revenue": retail_popups_revenue,
        "Retail Net Revenue": retail_net_revenue,  # ✅ Fixed: Now summing Retail + Pop-ups
        "Wholesale Net Revenue": wholesale_revenue,
    }

def calculate_marketing_spend(spend_df, start_date, end_date, online_revenue, new_customers):
    """Calculates Online Marketing Spend, Cost of Sale (COS%), and nCAC."""

    if spend_df is None:
        return 0, 0, 0  # No data → return zeros

    # ✅ Filter for date range
    filtered_spend_df = spend_df[(spend_df["Date"] >= start_date) & (spend_df["Date"] <= end_date)]
    
    online_marketing_spend = filtered_spend_df["Total Spend"].sum()
    online_cost_of_sale = round((online_marketing_spend / online_revenue) * 100, 3) if online_revenue > 0 else 0
    nCAC = (0.70 * online_marketing_spend / new_customers) if new_customers > 0 else 0

    return online_marketing_spend, online_cost_of_sale, nCAC

def calculate_growth(current_revenue, last_year_revenue):
    """
    Calculates the percentage growth between the current year's revenue and last year's revenue.
    
    Formula: ((current - last year) / last year) * 100

    Args:
    - current_revenue (float): Revenue for the current period
    - last_year_revenue (float): Revenue for the previous year

    Returns:
    - float: Growth percentage (rounded to 2 decimals)
    """
    if last_year_revenue is None or last_year_revenue == 0:
        return 0  # Avoid division by zero

    try:
        growth = ((current_revenue - last_year_revenue) / last_year_revenue) * 100
        return round(growth, 2)
    except Exception as e:
        print(f"❌ Error calculating growth: {e}")
        return 0

### ✅ **Get latest full week and print metrics**
latest_week_values = get_latest_full_week()

# Ensure correct unpacking of values
if isinstance(latest_week_values, dict) and "current_week" in latest_week_values:
    latest_week_start, latest_week_end = latest_week_values["current_week"]
else:
    raise ValueError("❌ Unexpected output format from `get_latest_full_week()`")

# ✅ Load data
data = load_data()
spend_data = load_spend_data()

# ✅ Calculate Revenue Metrics (Including Retail & Wholesale)
revenue_metrics = calculate_revenue_metrics(data, latest_week_start, latest_week_end)

# ✅ Get Unique Order Count
total_orders = deduplicate_orders(data, latest_week_start, latest_week_end)

