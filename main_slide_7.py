import os
import sys

# ✅ Ensure the scripts folder is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts")))

# ✅ Import the respective modules to trigger
from scripts.prepare.prepare_men_category import calculate_men_category_revenue
from scripts.final.finalized_men_category import sort_and_save_men_category_data
from scripts.excel.men_category_excel import update_men_category_excel

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)
RAW_MEN_CATEGORY_FILE = os.path.join(BASE_DIR, "data", "raw", "men_category_revenue_raw.csv")
FINALIZED_MEN_CATEGORY_FILE = os.path.join(BASE_DIR, "data", "final", "men_category_revenue_final.csv")

### 📊 Step 1: Run Men Category Revenue Preparation ###
print("\n📊 Running Men Category Revenue Preparation Script...")
os.system(f"python3 scripts/prepare/prepare_men_category.py")

### 🔍 Step 2: Run Men Category Formatting & Sorting ###
print("\n🔍 Running Men Category Formatting & Sorting Script...")
os.system(f"python3 scripts/final/finalized_men_category.py")

### 📊 Step 3: Run Men Category Excel Update ###
print("\n📊 Running Men Category Excel Update Script...")
os.system(f"python3 scripts/excel/men_category_excel.py")

print("\n🎉 **Slide 7 Process Completed Successfully!**")
