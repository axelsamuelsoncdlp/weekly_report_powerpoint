import os

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)

### 📊 Step 1: Run Conversion Markets Data Preparation ###
print("\n📊 Running Conversion Markets Data Preparation Script...")
os.system("python3 scripts/prepare/prepare_conversion_markets.py")

### 🔍 Step 2: Run Conversion Markets Finalization ###
print("\n🔍 Running Conversion Markets Finalization Script...")
os.system("python3 scripts/final/finalized_conversion_markets.py")

### 📊 Step 3: Run Conversion Markets Excel Update ###
print("\n📊 Running Conversion Markets Excel Update Script...")
os.system("python3 scripts/excel/conversion_markets_excel.py")

print("\n🎉 **Slide 13 Process Completed Successfully!** 🚀")
