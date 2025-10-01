import os
import pandas as pd

def finalize_top_products():
    """Ranks the top 20 products based on Gross Revenue, sums up duplicates, adds Total rows, and calculates SOB%."""

    # ✅ Define file paths
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    RAW_CSV_FILE = os.path.join(BASE_DIR, "data/raw/products_new_raw.csv")
    FINAL_CSV_FILE = os.path.join(BASE_DIR, "data/final/products_new_final.csv")

    # ✅ Ensure the raw CSV file exists
    if not os.path.exists(RAW_CSV_FILE):
        raise FileNotFoundError(f"❌ File not found: {RAW_CSV_FILE}")

    # ✅ Load the raw data
    df = pd.read_csv(RAW_CSV_FILE)

    # ✅ Debug: Print loaded data info
    print(f"\n📊 **Loaded Raw Data Shape:** {df.shape}")
    print(f"🔍 **Columns:** {list(df.columns)}")

    # ✅ Ensure required columns exist
    required_columns = {"Gender", "Category", "Product", "Color", "Gross Revenue", "Sales Qty"}
    if not required_columns.issubset(df.columns):
        print(f"❌ Missing required columns in dataset: {required_columns - set(df.columns)}")
        return None

    # ✅ Remove rows where any of the key grouping columns contain `"-"`
    df_filtered = df[~df[["Gender", "Category", "Product", "Color"]].apply(lambda row: "-" in row.values, axis=1)]

    print(f"\n🔍 **Filtered Out Rows with '-' Values. New Shape:** {df_filtered.shape}")

    # ✅ Convert Gross Revenue and Sales Qty to numeric (handles any non-numeric values)
    df_filtered["Gross Revenue"] = pd.to_numeric(df_filtered["Gross Revenue"], errors="coerce")
    df_filtered["Sales Qty"] = pd.to_numeric(df_filtered["Sales Qty"], errors="coerce")

    # ✅ Group by Gender, Category, Product, and Color, summing Gross Revenue and Sales Qty
    df_grouped = df_filtered.groupby(["Gender", "Category", "Product", "Color"], as_index=False).agg({
        "Gross Revenue": "sum",
        "Sales Qty": "sum"
    })

    # ✅ Calculate Grand Total for all products (used for SOB%)
    grand_total_gross_revenue = df_grouped["Gross Revenue"].sum()
    grand_total_sales_qty = df_grouped["Sales Qty"].sum()

    # ✅ Rank top 20 products by Gross Revenue
    df_top = df_grouped.sort_values(by="Gross Revenue", ascending=False).head(20)

    # ✅ Add `Rank` column
    df_top.insert(0, "Rank", range(1, len(df_top) + 1))

    # ✅ Calculate SOB% for top 20 products
    df_top["SOB%"] = (df_top["Gross Revenue"] / grand_total_gross_revenue) * 100

    # ✅ Calculate total for top 20 products
    top_20_gross_revenue = df_top["Gross Revenue"].sum()
    top_20_sales_qty = df_top["Sales Qty"].sum()
    top_20_sob = (top_20_gross_revenue / grand_total_gross_revenue) * 100  # ✅ SOB% for Top 20 Total

    # ✅ Create "Top 20 Total" row
    total_row_top_20 = pd.DataFrame([{
        "Rank": "Top 20 Total",
        "Gender": "",
        "Category": "",
        "Product": "",
        "Color": "",
        "Gross Revenue": top_20_gross_revenue,
        "Sales Qty": top_20_sales_qty,
        "SOB%": top_20_sob
    }])

    # ✅ Create "Grand Total" row (SOB% should be 100%)
    total_row_all = pd.DataFrame([{
        "Rank": "Grand Total",
        "Gender": "",
        "Category": "",
        "Product": "",
        "Color": "",
        "Gross Revenue": grand_total_gross_revenue,
        "Sales Qty": grand_total_sales_qty,
        "SOB%": 100.0
    }])

    # ✅ Append both total rows to DataFrame
    df_final = pd.concat([df_top, total_row_top_20, total_row_all], ignore_index=True)

    # ✅ Format SOB% as a percentage with 2 decimal places
    df_final["SOB%"] = df_final["SOB%"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "-")

    # ✅ Reset index for clarity
    df_final.reset_index(drop=True, inplace=True)

    print("\n🏆 **Top 20 Products Ranked by Gross Revenue (With SOB% & Total Rows):**")
    print(df_final.tail(5))  # ✅ Print last 5 rows to verify the total rows

    # ✅ Define the output directory and ensure it exists
    output_dir = os.path.join(BASE_DIR, "data/final")
    os.makedirs(output_dir, exist_ok=True)

    # ✅ Save to CSV
    df_final.to_csv(FINAL_CSV_FILE, index=False)
    
    print(f"\n📂 **Saved top 20 products with totals & SOB% to:** {FINAL_CSV_FILE}")

    return df_final  # ✅ Return the ranked DataFrame with total rows

# ✅ Run script
if __name__ == "__main__":
    finalize_top_products()