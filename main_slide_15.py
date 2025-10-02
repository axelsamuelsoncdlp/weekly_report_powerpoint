import os

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)

### 📊 Step 1: Run Returning Customers Markets Data Preparation ###
print("\n📊 Running Returning Customers Markets Data Preparation Script...")
os.system("python3 scripts/prepare/prepare_returning_customers_markets.py")

### 🔍 Step 2: Run Returning Customers Markets Finalization ###
print("\n🔍 Running Returning Customers Markets Finalization Script...")
os.system("python3 scripts/final/finalized_returning_customers_markets.py")

### 📊 Step 3: Run Returning Customers Markets Excel Update ###
print("\n📊 Running Returning Customers Markets Excel Update Script...")
os.system("python3 scripts/excel/returning_customers_markets_excel.py")

print("\n🎉 **Slide 15 Process Completed Successfully!** 🚀")
