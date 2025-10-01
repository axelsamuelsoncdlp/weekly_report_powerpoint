import os
import sys

# ✅ Ensure the scripts folder is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts")))

# ✅ Import the respective modules to trigger
from scripts.prepare.prepare_gender import calculate_gender_revenue
from scripts.final.finalized_gender import sort_and_save_gender_data
from scripts.excel.gender_excel import update_gender_excel

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)
RAW_GENDER_FILE = os.path.join(BASE_DIR, "data", "raw", "gender_revenue_raw.csv")
FINALIZED_GENDER_FILE = os.path.join(BASE_DIR, "data", "final", "gender_revenue_final.csv")

### 📊 Step 1: Run Gender Revenue Preparation ###
print("\n📊 Running Gender Revenue Preparation Script...")
os.system(f"python3 scripts/prepare/prepare_gender.py")

### 🔍 Step 2: Run Gender Revenue Formatting & Sorting ###
print("\n🔍 Running Gender Revenue Formatting & Sorting Script...")
os.system(f"python3 scripts/final/finalized_gender.py")

### 📊 Step 3: Run Gender Revenue Excel Update ###
print("\n📊 Running Gender Revenue Excel Update Script...")
os.system(f"python3 scripts/excel/gender_excel.py")

print("\n🎉 **Slide 6 Process Completed Successfully!**")