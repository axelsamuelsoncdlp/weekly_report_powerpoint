import sys
import os
import pandas as pd

# Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculator.metrics_calculator import load_data

# ✅ Load dataset
data = load_data()

# ✅ Remove invalid Gender values
data = data[data["Gender"] != "-"]

# ✅ Normalize Gender and Category text
data["Gender"] = data["Gender"].str.strip().str.upper()
data["Category"] = data["Category"].str.strip().str.upper()

# ✅ Filter for MEN
men_data = data[data["Gender"] == "MEN"]

# ✅ Select only required columns
men_data_selected = men_data[["Gender", "Category", "Gross Revenue (ex. VAT)"]]

# ✅ Print first 5 rows
print("\n📊 **Filtered Data for MEN (Gender, Category, Gross Revenue):**")
print(men_data_selected.head())
