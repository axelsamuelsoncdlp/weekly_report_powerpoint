import os

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)

### 📊 Step 1: Run Sessions Markets Data Preparation ###
print("\n📊 Running Sessions Markets Data Preparation Script...")
os.system("python3 scripts/prepare/prepare_sessions_markets.py")

### 🔍 Step 2: Run Sessions Markets Finalization ###
print("\n🔍 Running Sessions Markets Finalization Script...")
os.system("python3 scripts/final/finalized_sessions_markets.py")

### 📊 Step 3: Run Sessions Markets Excel Update ###
print("\n📊 Running Sessions Markets Excel Update Script...")
os.system("python3 scripts/excel/sessions_markets_excel.py")

print("\n🎉 **Slide 12 Process Completed Successfully!** 🚀")
