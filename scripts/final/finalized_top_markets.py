import pandas as pd
import os
import numpy as np

# Define file paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
TOP_MARKETS_FILE = os.path.join(BASE_DIR, "data", "raw", "top_markets_raw.csv")
TOP_MARKETS_PRY_FILE = os.path.join(BASE_DIR, "data", "raw", "top_markets_pry_raw.csv")
FINAL_OUTPUT_DIR = os.path.join(BASE_DIR, "data", "final")

# Ensure the final output directory exists
os.makedirs(FINAL_OUTPUT_DIR, exist_ok=True)

TOP_MARKETS_FINAL_FILE = os.path.join(FINAL_OUTPUT_DIR, "top_markets_final.csv")
TOP_MARKETS_GROWTH_FINAL_FILE = os.path.join(FINAL_OUTPUT_DIR, "top_markets_growth_final.csv")
TOP_MARKETS_SHARE_FINAL_FILE = os.path.join(FINAL_OUTPUT_DIR, "top_markets_share_final.csv")

def rename_columns(df):
    """Renames week columns to just numbers (e.g., 'Vecka 51 (2024)' → '51')."""
    new_columns = {col: ''.join(filter(str.isdigit, col.split()[1])) for col in df.columns if "Vecka" in col}
    df = df.rename(columns=new_columns)
    return df

def extract_gross_revenue(file_path):
    """Extracts Gross Revenue for the top 15 markets, ROW, and Total for the last 8 weeks."""
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found -> {file_path}")
        return pd.DataFrame()

    df = pd.read_csv(file_path)

    if "Market" not in df.columns or "Metric" not in df.columns:
        print(f"❌ Error: Missing required columns in {file_path}")
        return pd.DataFrame()

    gross_revenue_df = df[df["Metric"] == "Online Gross Revenue"]
    if gross_revenue_df.empty:
        print(f"⚠️ Warning: No Gross Revenue data found in {file_path}")
        return pd.DataFrame()

    week_columns = [col for col in df.columns if "Vecka" in col][-8:]

    if not week_columns:
        print(f"⚠️ Warning: No revenue columns found in {file_path}")
        return pd.DataFrame()

    gross_revenue_df = gross_revenue_df.copy()
    
    # Convert all week columns to numeric, replacing non-numeric values with NaN
    for col in week_columns:
        gross_revenue_df[col] = pd.to_numeric(gross_revenue_df[col], errors='coerce')
    
    gross_revenue_df["8-week avg"] = gross_revenue_df[week_columns].mean(axis=1, skipna=True)

    top_markets = gross_revenue_df.nlargest(15, "8-week avg")["Market"].tolist()
    top_markets += ["ROW", "Total"]

    gross_revenue_df = gross_revenue_df[gross_revenue_df["Market"].isin(top_markets)]
    result_df = gross_revenue_df[["Market"] + week_columns + ["8-week avg"]].copy()
    result_df = rename_columns(result_df)

    return result_df

def extract_gross_revenue_current_year():
    """Extract Gross Revenue for the Current Year"""
    return extract_gross_revenue(TOP_MARKETS_FILE)

def extract_gross_revenue_last_year():
    """Extract Gross Revenue for Last Year"""
    return extract_gross_revenue(TOP_MARKETS_PRY_FILE)

def calculate_revenue_growth(df_current, df_last_year):
    """Calculates revenue growth percentage ((CY/LY) - 1) * 100 for each week and the 8-week avg."""
    if df_current.empty or df_last_year.empty:
        print("⚠️ Warning: Missing data for one of the years. Skipping growth calculation.")
        return pd.DataFrame()

    growth_df = df_current.merge(df_last_year, on="Market", suffixes=(" (CY)", " (LY)"), how="left")
    
    # Fill missing values with 0 for markets that don't exist in last year
    numeric_columns = growth_df.select_dtypes(include=[np.number]).columns
    growth_df[numeric_columns] = growth_df[numeric_columns].fillna(0)

    week_columns_cy = [col for col in growth_df.columns if "(CY)" in col and "8-week avg" not in col]
    week_columns_ly = [col for col in growth_df.columns if "(LY)" in col and "8-week avg" not in col]

    if not week_columns_cy or not week_columns_ly:
        print(f"❌ Error: Missing expected columns in DataFrame: {week_columns_cy + week_columns_ly}")
        return pd.DataFrame()

    for week_cy in week_columns_cy:
        week_ly = week_cy.replace(" (CY)", " (LY)")
        growth_column = week_cy.replace(" (CY)", "")  # Keep original column name

        if week_cy not in growth_df.columns or week_ly not in growth_df.columns:
            continue  

        growth_df[growth_column] = growth_df.apply(
            lambda row: ((row[week_cy] / row[week_ly] - 1) * 100) if row[week_ly] != 0 else 0, axis=1
        )

    # For 8-week avg, use current week vs last year same week (not 8-week averages)
    if "39 (CY)" in growth_df.columns and "39 (LY)" in growth_df.columns:
        growth_df["8-week avg"] = growth_df.apply(
            lambda row: ((row["39 (CY)"] / row["39 (LY)"] - 1) * 100) if row["39 (LY)"] != 0 else 0, axis=1
        )

    final_columns = ["Market"] + [col for col in growth_df.columns if "(LY)" not in col and "(CY)" not in col and col != "Market"]
    growth_df = growth_df[final_columns]

    return format_percentage(growth_df)

def calculate_revenue_share(df_current):
    """Calculates the share of revenue for each market based on total revenue."""
    if df_current.empty:
        print("⚠️ Warning: No data available for revenue share calculation.")
        return df_current

    df_share = df_current.copy()
    total_revenue = df_share[df_share["Market"] == "Total"].iloc[:, 1:].values  # Extract total revenue row

    if total_revenue.size == 0:
        print("❌ Error: Total revenue row not found. Cannot calculate revenue share.")
        return pd.DataFrame()

    df_share.iloc[:, 1:] = df_share.iloc[:, 1:].div(total_revenue, axis=1) * 100

    return format_percentage(df_share)

def format_revenue(df):
    """Formats revenue values to thousands and rounds up."""
    if df.empty:
        print("⚠️ Warning: No data available for formatting.")
        return df

    formatted_df = df.copy()
    numeric_columns = [col for col in df.columns if col.isdigit() or "8-week avg" in col]
    formatted_df[numeric_columns] = np.ceil(formatted_df[numeric_columns] / 1000).astype(int)

    return formatted_df

def format_percentage(df):
    """Formats percentage values: rounds normally, removes decimals, and applies parentheses for negatives."""
    formatted_df = df.copy()

    def format_value(val):
        try:
            val = float(val)  # ✅ Ensure conversion to float
            val = round(val)  # ✅ Normal rounding instead of always rounding up
            return f"({abs(int(val))})" if val < 0 else str(int(val))  # ✅ Format negatives in parentheses
        except (ValueError, TypeError):
            return val  

    # Apply formatting to all numeric columns
    for col in formatted_df.columns[1:]:  # Skip 'Market' column
        formatted_df[col] = formatted_df[col].apply(format_value)

    return formatted_df

def finalize_top_markets():
    """Runs the finalized processing for Top Markets data and saves outputs."""
    
    # Run calculations
    gross_revenue_current_year_df = extract_gross_revenue_current_year()
    gross_revenue_last_year_df = extract_gross_revenue_last_year()
    revenue_growth_df = calculate_revenue_growth(gross_revenue_current_year_df, gross_revenue_last_year_df)

    # Format revenue data
    formatted_gross_revenue_current_year_df = format_revenue(gross_revenue_current_year_df)

    # **Calculate and Format Revenue Share**
    revenue_share_df = calculate_revenue_share(gross_revenue_current_year_df)

    # Sort revenue data: markets by Current Week (vecka 39) descending, then ROW on row 17 and Total on row 18
    # First, get all markets except Total and ROW, sorted by Current Week (vecka 39) descending
    markets_only = formatted_gross_revenue_current_year_df[~formatted_gross_revenue_current_year_df["Market"].isin(["Total", "ROW"])].sort_values("39", ascending=False)
    
    # Get ROW and Total separately
    row_data = formatted_gross_revenue_current_year_df[formatted_gross_revenue_current_year_df["Market"] == "ROW"]
    total_data = formatted_gross_revenue_current_year_df[formatted_gross_revenue_current_year_df["Market"] == "Total"]
    
    # Combine: markets (sorted by Current Week) + ROW + Total
    formatted_gross_revenue_current_year_df = pd.concat([markets_only, row_data, total_data], ignore_index=True)
    
    # Save Gross Revenue Data
    formatted_gross_revenue_current_year_df.to_csv(TOP_MARKETS_FINAL_FILE, index=False)

    # **Sort growth data to match revenue order: markets by Current Week (vecka 39) descending, then ROW on row 17 and Total on row 18**
    if "Market" in revenue_growth_df.columns:
        # First, get all markets except Total and ROW, sorted by Current Week (same order as revenue data)
        markets_only = revenue_growth_df[~revenue_growth_df["Market"].isin(["Total", "ROW"])]
        
        # Get ROW and Total separately
        row_data = revenue_growth_df[revenue_growth_df["Market"] == "ROW"]
        total_data = revenue_growth_df[revenue_growth_df["Market"] == "Total"]
        
        # Combine: markets (same order as revenue) + ROW + Total
        revenue_growth_df = pd.concat([markets_only, row_data, total_data], ignore_index=True)
        revenue_growth_df = revenue_growth_df.drop(columns=["Market"])

    # Save Growth Data WITHOUT "Market" column
    revenue_growth_df.to_csv(TOP_MARKETS_GROWTH_FINAL_FILE, index=False)

    # **Sort share data to match revenue order: markets by Current Week (vecka 39) descending, then ROW on row 17 and Total on row 18**
    if "Market" in revenue_share_df.columns:
        # First, get all markets except Total and ROW, sorted by Current Week (same order as revenue data)
        markets_only = revenue_share_df[~revenue_share_df["Market"].isin(["Total", "ROW"])]
        
        # Get ROW and Total separately
        row_data = revenue_share_df[revenue_share_df["Market"] == "ROW"]
        total_data = revenue_share_df[revenue_share_df["Market"] == "Total"]
        
        # Combine: markets (same order as revenue) + ROW + Total
        revenue_share_df = pd.concat([markets_only, row_data, total_data], ignore_index=True)
        revenue_share_df = revenue_share_df.drop(columns=["Market"])

    # Save Revenue Share Data WITHOUT "Market" column
    revenue_share_df.to_csv(TOP_MARKETS_SHARE_FINAL_FILE, index=False)

    print("\n✅ **All Top Markets data finalized and saved successfully!**")