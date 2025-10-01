import os
import sys

# ✅ Ensure the scripts folder is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts")))

# ✅ Import the respective modules to trigger
from scripts.prepare.prepare_women_category import calculate_women_category_revenue
from scripts.final.finalized_women_category import sort_and_save_women_category_data
from scripts.excel.women_category_excel import update_women_category_excel

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)
RAW_WOMEN_CATEGORY_FILE = os.path.join(BASE_DIR, "data", "raw", "women_category_revenue_raw.csv")
FINALIZED_WOMEN_CATEGORY_FILE = os.path.join(BASE_DIR, "data", "final", "women_category_revenue_final.csv")

### 📊 Step 1: Run Women Category Revenue Preparation ###
print("\n📊 Running Women Category Revenue Preparation Script...")
os.system(f"python3 scripts/prepare/prepare_women_category.py")

### 🔍 Step 2: Run Women Category Formatting & Sorting ###
print("\n🔍 Running Women Category Formatting & Sorting Script...")
os.system(f"python3 scripts/final/finalized_women_category.py")

### 📊 Step 3: Run Women Category Excel Update ###
print("\n📊 Running Women Category Excel Update Script...")
os.system(f"python3 scripts/excel/women_category_excel.py")

print("\n🎉 **Slide 8 Process Completed Successfully!**")