import pandas as pd

# Filens sökväg
file_path = "/Users/axelsamuelson/Documents/CDLP_code/weekly_reports/data/formatted/weekly_data_formatted.csv"

# Läs in CSV-filen
df = pd.read_csv(file_path, parse_dates=["Date"], low_memory=False)

# Skapa en kolumn för köpår
df["Year"] = df["Date"].dt.year

# Filtrera för endast åren 2020-2024
df = df[df["Year"].between(2020, 2024)]

# Gruppera kunder per år
customers_per_year = df.groupby("Year")["Customer E-mail"].unique().to_dict()

# Beräkna churn rate och retention rate mellan 2020 och 2024
churn_rates = {}
retention_rates = {}

for year in range(2020, 2024):  # Loopar mellan 2020 och 2023 (churn beräknas från ett år till nästa)
    current_year_customers = set(customers_per_year.get(year, []))
    next_year_customers = set(customers_per_year.get(year + 1, []))
    
    churned_customers = current_year_customers - next_year_customers
    total_customers = len(current_year_customers | next_year_customers)
    
    churn_rate = len(churned_customers) / total_customers if total_customers > 0 else 0
    retention_rate = 1 - churn_rate

    churn_rates[f"{year}-{year+1}"] = churn_rate
    retention_rates[f"{year}-{year+1}"] = retention_rate

# Skriv ut churn och retention rates mellan 2020 och 2024
for period in churn_rates.keys():
    print(f"{period} - Churn Rate: {churn_rates[period]:.2%}, Retention Rate: {retention_rates[period]:.2%}")
