import os
import sys
import pandas as pd

# Ensure the scripts folder is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import necessary functions
from calculator.metrics_calculator import load_data
from calculator.date_utils import get_latest_full_week

# Define output file path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
AUDIT_OUTPUT_PATH = os.path.join(BASE_DIR, "data", "audit", "wholesale_revenue_audit.csv")

# Ensure output directory exists
os.makedirs(os.path.dirname(AUDIT_OUTPUT_PATH), exist_ok=True)

def audit_wholesale_revenue():
    """Audits the presence and calculation of Wholesale Net Revenue using Channel Group."""
    df = load_data()
    time_periods = get_latest_full_week()

    print("\n🔍 DEBUG: Checking available columns in raw data:")
    print(df.columns)

    if "Channel Group" not in df.columns or "Gross Revenue (ex. VAT)" not in df.columns:
        print("❌ Required columns ('Channel Group' or 'Gross Revenue (ex. VAT)') are missing from the dataset!")
        return

    audit_results = []
    for period_name, (start, end) in time_periods.items():
        period_df = df[(df["Date"] >= start) & (df["Date"] <= end)]

        # ✅ Filter only Wholesale sales
        wholesale_df = period_df[period_df["Channel Group"].str.lower() == "wholesale"]
        wholesale_revenue = wholesale_df["Gross Revenue (ex. VAT)"].sum()

        print(f"\n📆 Auditing Wholesale Net Revenue for {period_name} ({start} to {end})")
        print(f"🔍 Total Wholesale Revenue: {wholesale_revenue:.2f}")

        audit_results.append({
            "Period": period_name,
            "Start Date": start,
            "End Date": end,
            "Wholesale Net Revenue": wholesale_revenue
        })

    # Save the audit results
    audit_df = pd.DataFrame(audit_results)
    audit_df.to_csv(AUDIT_OUTPUT_PATH, index=False)
    print(f"\n✅ Wholesale Revenue Audit saved to: {AUDIT_OUTPUT_PATH}")

if __name__ == "__main__":
    audit_wholesale_revenue()