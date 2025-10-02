import os

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)

### 📊 Step 1: Run AOV Returning Markets Data Preparation ###
print("\n📊 Running AOV Returning Markets Data Preparation Script...")
os.system("python3 scripts/prepare/prepare_aov_returning_markets.py")

### 🔍 Step 2: Run AOV Returning Markets Finalization ###
print("\n🔍 Running AOV Returning Markets Finalization Script...")
os.system("python3 scripts/final/finalized_aov_returning_markets.py")

### 📊 Step 3: Run AOV Returning Markets Excel Update ###
print("\n📊 Running AOV Returning Markets Excel Update Script...")
os.system("python3 scripts/excel/aov_returning_markets_excel.py")

print("\n🎉 **Slide 17 Process Completed Successfully!** 🚀")
