import os

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)

### 📊 Step 1: Run AOV New Markets Data Preparation ###
print("\n📊 Running AOV New Markets Data Preparation Script...")
os.system("python3 scripts/prepare/prepare_aov_new_markets.py")

### 🔍 Step 2: Run AOV New Markets Finalization ###
print("\n🔍 Running AOV New Markets Finalization Script...")
os.system("python3 scripts/final/finalized_aov_new_markets.py")

### 📊 Step 3: Run AOV New Markets Excel Update ###
print("\n📊 Running AOV New Markets Excel Update Script...")
os.system("python3 scripts/excel/aov_new_markets_excel.py")

print("\n🎉 **Slide 16 Process Completed Successfully!** 🚀")
