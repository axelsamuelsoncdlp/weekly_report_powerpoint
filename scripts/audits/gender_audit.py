import os
import pandas as pd

# Definiera sökvägen till filen
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "formatted", "weekly_data_formatted.csv")

# Ladda in data
df = pd.read_csv(DATA_PATH, low_memory=False)

# Konvertera 'Date'-kolumnen till datetime-format
df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

# Filtrera efter datumintervallet 2025-02-03 till 2025-02-09
start_date = pd.to_datetime("2025-02-03").date()
end_date = pd.to_datetime("2025-02-09").date()
df_filtered = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

# Filtrera endast "Online" kanal
df_filtered = df_filtered[df_filtered["Channel Group"] == "Online"]

# Välj specifika kolumner
selected_columns = [
    "Channel Group", "Order Id", "Orders", "Gross Revenue (ex. VAT)",
    "Gender", "Category", "Product", "Color", "Sales Qty"
]

# Kontrollera att alla kolumner finns i datasetet
available_columns = df_filtered.columns.tolist()
missing_columns = [col for col in selected_columns if col not in available_columns]

if missing_columns:
    print(f"⚠️ Följande kolumner saknas i datasetet: {missing_columns}")
else:
    # Skapa en DataFrame med de valda kolumnerna
    df_selected = df_filtered[selected_columns]

    # Summera Gross Revenue (ex. VAT) och avrunda till heltal
    total_revenue = round(df_selected["Gross Revenue (ex. VAT)"].sum())

    # Summera Gross Revenue (ex. VAT) per kön
    gender_summary = df_selected.groupby("Gender")["Gross Revenue (ex. VAT)"].sum().reset_index()
    gender_summary["Gross Revenue (ex. VAT)"] = gender_summary["Gross Revenue (ex. VAT)"].round().astype(int)

    # Skapa summeringsraden för TOTAL
    summary_row = pd.DataFrame(
        {
            "Channel Group": ["TOTAL"],
            "Order Id": [""],
            "Orders": [""],
            "Gross Revenue (ex. VAT)": [total_revenue],
            "Gender": [""],
            "Category": [""],
            "Product": [""],
            "Color": [""],
            "Sales Qty": [""]
        }
    )

    # Lägg till summeringsraden längst ner
    df_final = pd.concat([df_selected.head(20), summary_row], ignore_index=True)

    # Formatera alla numeriska kolumner som heltal (ingen decimal)
    numeric_columns = ["Orders", "Gross Revenue (ex. VAT)", "Sales Qty"]
    for col in numeric_columns:
        if col in df_final.columns:
            df_final[col] = pd.to_numeric(df_final[col], errors="coerce").fillna(0).astype(int)

    # Visa resultatet
    print(df_final)
    
    # Skriva ut summeringen per kön
    print("\n🔹 Summering av Gross Revenue (ex. VAT) per Gender:")
    print(gender_summary)