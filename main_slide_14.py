import os

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)

### 📊 Step 1: Run New Customers Markets Data Preparation ###
print("\n📊 Running New Customers Markets Data Preparation Script...")
os.system("python3 scripts/prepare/prepare_new_customers_markets.py")

### 🔍 Step 2: Run New Customers Markets Finalization ###
print("\n🔍 Running New Customers Markets Finalization Script...")
os.system("python3 scripts/final/finalized_new_customers_markets.py")

### 📊 Step 3: Run New Customers Markets Excel Update ###
print("\n📊 Running New Customers Markets Excel Update Script...")
os.system("python3 scripts/excel/new_customers_markets_excel.py")

print("\n🎉 **Slide 14 Process Completed Successfully!** 🚀")