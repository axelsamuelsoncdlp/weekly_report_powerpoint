import os

# ✅ Define file paths
BASE_DIR = os.path.dirname(__file__)

### 📊 Step 1: Run Online Media Spend Data Preparation ###
print("\n📊 Running Online Media Spend Data Preparation Script...")
os.system("python3 scripts/prepare/prepare_online_media_spend.py")

### 🔍 Step 2: Run Online Media Spend Finalization ###
print("\n🔍 Running Online Media Spend Finalization Script...")
os.system("python3 scripts/final/finalized_online_media_spend.py")

### 📊 Step 3: Run Online Media Spend Excel Update ###
print("\n📊 Running Online Media Spend Excel Update Script...")
os.system("python3 scripts/excel/online_media_spend_excel.py")

print("\n🎉 **Slide 18 Process Completed Successfully!** 🚀")
