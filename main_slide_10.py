import os

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)

### 📊 Step 1: Run New Customers' Products Data Preparation ###
print("\n📊 Running New Customers' Products Data Preparation Script...")
os.system("python3 scripts/prepare/prepare_products_new.py")

### 🔍 Step 2: Run New Customers' Products Finalization ###
print("\n🔍 Running New Customers' Products Finalization Script...")
os.system("python3 scripts/final/finalized_products_new.py")

### 📊 Step 3: Run New Customers' Products Excel Update ###
print("\n📊 Running New Customers' Products Excel Update Script...")
os.system("python3 scripts/excel/products_new_excel.py")

### 📊 Step 4: Run Returning Customers' Products Data Preparation ###
print("\n📊 Running Returning Customers' Products Data Preparation Script...")
os.system("python3 scripts/prepare/prepare_products_returning.py")

### 🔍 Step 5: Run Returning Customers' Products Finalization ###
print("\n🔍 Running Returning Customers' Products Finalization Script...")
os.system("python3 scripts/final/finalized_products_returning.py")

### 📊 Step 6: Run Returning Customers' Products Excel Update ###
print("\n📊 Running Returning Customers' Products Excel Update Script...")
os.system("python3 scripts/excel/products_returning_excel.py")

print("\n🎉 **Slide 11 Process Completed Successfully!** 🚀")