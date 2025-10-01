import os

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)

### 📊 Step 1: Run Gender & Category Revenue Preparation ###
print("\n📊 Running Gender & Category Revenue Calculation Script...")
os.system("python3 scripts/prepare/prepare_gender_category.py")

### 📊 Step 1.2: Run Gender & Category Revenue Preparation ###
print("\n📊 Running Gender & Category Revenue Calculation Script...")
os.system("python3 scripts/prepare/prepare_gender_category_ly.py")

### 🔍 Step 2: Run Gender & Category Revenue Formatting ###
print("\n🔍 Running Gender & Category Revenue Formatting & Sorting Script...")
os.system("python3 scripts/final/finalized_gender_category.py")

### 🔍 Step 2: Run Gender & Category Revenue Formatting ###
print("\n🔍 Running Gender & Category Revenue Formatting & Sorting Script...")
os.system("python3 scripts/final/finalized_gender_category_ly.py")

### 🔍 Step 3: Run Gender & Category Growth Calculation ###
print("\n📊 Running Gender & Category Growth Calculation Script...")
os.system("python3 scripts/final/finalized_gender_category_growth.py")

### 🔍 Step 4: Run Gender & Category Share of Revenue Calculation (SoB) ###
print("\n📊 Running Gender & Category Share of Revenue Calculation Script...")
os.system("python3 scripts/final/finalized_gender_category_sob.py")

### 📊 Step 5: Update Gender & Category Revenue in Excel ###
print("\n📊 Running Gender & Category Revenue Excel Update Script...")
os.system("python3 scripts/excel/gender_category_excel.py")

### 📊 Step 6: Update Gender & Category Growth in Excel ###
print("\n📊 Running Gender & Category Growth Excel Update Script...")
os.system("python3 scripts/excel/gender_category_growth_excel.py")

### 📊 Step 7: Update Gender & Category Share of Revenue (SoB) in Excel ###
print("\n📊 Running Gender & Category Share of Revenue (SoB) Excel Update Script...")
os.system("python3 scripts/excel/gender_category_sob_excel.py")

print("\n🎉 **Slide 9 Process Completed Successfully!** 🚀")