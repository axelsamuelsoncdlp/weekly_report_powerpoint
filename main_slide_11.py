import os

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)

### 📊 Step 1: Run Men's Products Data Preparation ###
print("\n📊 Running Men's Products Data Preparation Script...")
os.system("python3 scripts/prepare/prepare_products_men.py")

### 🔍 Step 2: Run Men's Products Finalization ###
print("\n🔍 Running Men's Products Finalization Script...")
os.system("python3 scripts/final/finalized_products_men.py")

### 📊 Step 3: Run Men's Products Excel Update ###
print("\n📊 Running Men's Products Excel Update Script...")
os.system("python3 scripts/excel/products_men_excel.py")

### 📊 Step 4: Run Women's Products Data Preparation ###
print("\n📊 Running Women's Products Data Preparation Script...")
os.system("python3 scripts/prepare/prepare_products_women.py")

### 🔍 Step 5: Run Women's Products Finalization ###
print("\n🔍 Running Women's Products Finalization Script...")
os.system("python3 scripts/final/finalized_products_women.py")

### 📊 Step 6: Run Women's Products Excel Update ###
print("\n📊 Running Women's Products Excel Update Script...")
os.system("python3 scripts/excel/products_women_excel.py")

print("\n🎉 **Slide 10 Process Completed Successfully!** 🚀")