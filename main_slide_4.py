import os
import sys

# ✅ Ensure the scripts folder is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts")))

# ✅ Import the respective modules to trigger
from scripts.prepare.prepare_online_kpis import calculate_kpis
from scripts.final.finalized_online_kpis import sort_and_save_kpi_data
from scripts.excel.online_kpis_excel import update_online_kpis_excel

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)
RAW_KPI_FILE = os.path.join(BASE_DIR, "data", "raw", "online_kpis_raw.csv")
FINALIZED_KPI_FILE = os.path.join(BASE_DIR, "data", "final", "online_kpis_final.csv")

### 📊 Step 1: Run KPI Preparation ###
print("\n📊 Running KPI Calculation Script...")
os.system(f"python3 scripts/prepare/prepare_online_kpis.py")

### 🔍 Step 2: Run KPI Formatting & Sorting ###
print("\n🔍 Running KPI Formatting & Sorting Script...")
os.system(f"python3 scripts/final/finalized_online_kpis.py")

### 📊 Step 3: Run KPI Excel Update ###
print("\n📊 Running KPI Excel Update Script...")
os.system(f"python3 scripts/excel/online_kpis_excel.py")

print("\n🎉 **Slide 4 Process Completed Successfully!**")