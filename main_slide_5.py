import os
import sys

# ✅ Ensure the scripts folder is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts")))

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)
RAW_CONTRIBUTION_FILE = os.path.join(BASE_DIR, "data", "raw", "contribution_raw.csv")
FINALIZED_CONTRIBUTION_FILE = os.path.join(BASE_DIR, "data", "final", "contribution_final.csv")

### 📊 Step 1: Run Contribution Data Preparation ###
print("\n📊 Running Contribution Data Preparation Script...")
os.system(f"python3 scripts/prepare/prepare_contribution.py")

### 🔍 Step 2: Run Contribution Data Formatting & Sorting ###
print("\n🔍 Running Contribution Data Formatting & Sorting Script...")
os.system(f"python3 scripts/final/finalized_contribution.py")

### 📊 Step 3: Run Contribution Excel Update ###
print("\n📊 Running Contribution Excel Update Script...")
os.system(f"python3 scripts/excel/contribution_excel.py")

print("\n🎉 **Slide 5 Process Completed Successfully!**")