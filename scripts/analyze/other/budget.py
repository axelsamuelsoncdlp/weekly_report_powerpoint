import sys
import os
import pandas as pd

# ✅ Importera load_data
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from calculator.metrics_calculator import load_data

# ✅ Ladda data
data = load_data()

# ✅ Kontrollera kolumner
required_columns = {"Date", "Customer E-mail", "Channel Group"}
missing = required_columns - set(data.columns)
if missing:
    raise KeyError(f"❌ Saknade kolumner: {missing}")

# ✅ Datum & Räkenskapsår
data["Date"] = pd.to_datetime(data["Date"])
data["Fiscal_Year"] = data["Date"].apply(lambda d: d.year + 1 if d.month >= 4 else d.year)

# ✅ Endast Online & giltiga e-mail
data = data[data["Channel Group"] == "Online"]
data = data.dropna(subset=["Customer E-mail"])

# ✅ Hitta cohort-år (första köp per kund)
cohort = data.groupby("Customer E-mail")["Fiscal_Year"].min().reset_index()
cohort.columns = ["Customer E-mail", "Cohort_Year"]

# ✅ Slå ihop cohort med originaldata
data = data.merge(cohort, on="Customer E-mail", how="left")

# ✅ Filtrera till år >= cohort (inga köp före första köp)
data = data[data["Fiscal_Year"] >= data["Cohort_Year"]]

# ✅ Räkna antal unika kunder från varje cohort per år
cohort_counts = data.groupby(["Cohort_Year", "Fiscal_Year"])["Customer E-mail"].nunique().unstack(fill_value=0)

# ✅ Hämta cohortstorlek (antal kunder första året)
cohort_sizes = pd.Series(
    [cohort_counts.loc[year, year] for year in cohort_counts.index],
    index=cohort_counts.index
)

# ✅ Dividera varje rad med cohortstorlek → retention i %
cohort_percent = cohort_counts.divide(cohort_sizes, axis=0).round(4) * 100
cohort_percent = cohort_percent.round(1)

# ✅ Skriv ut för kopiering
print("\n📋 Cohortanalys – retention rate (%) per år (endast Online)")
print(cohort_percent.to_csv(sep="\t", index=True))

# ✅ Exportera till budget_filer som CSV
output_dir = "/Users/axelsamuelson/Documents/budget_filer"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "cohort_retention_percent.csv")
cohort_percent.to_csv(output_path)

print(f"\n✅ Cohort retention-fil sparad till: {output_path}")
