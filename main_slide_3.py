import os
import sys
import time
import subprocess

# Ensure the scripts folder is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts")))

# Import necessary functions
from prepare.prepare_top_markets import load_and_prepare_top_markets  
from prepare.prepare_top_markets_pry import load_and_prepare_top_markets_pry  
from final.finalized_top_markets import finalize_top_markets  
from excel.top_markets_excel import update_excel_with_top_markets  
from macros.top_markets_macro import run_macro as run_top_markets_macro  
from calculator.date_utils import get_latest_full_week  
from calculator.define_markets import get_all_markets  
from calculator.metrics_calculator import calculate_revenue_metrics  

# Define file paths
BASE_DIR = os.path.dirname(__file__)
EXCEL_FILE_PATH = os.path.join(BASE_DIR, "macros", "top_table.xlsm")

### 📊 Step 1: Preparing Top Markets Data ###
print("\n📊 Step 1A: Preparing Top Markets Data")
load_and_prepare_top_markets()
load_and_prepare_top_markets_pry()
print("✅ Top Markets Data Processed")

### 🔍 Step 2: Finalizing Top Markets Data ###
print("\n🔍 Step 2: Finalizing Top Markets Data")
finalize_top_markets()
print("✅ Final Top Markets Data Processed")

### 📈 Step 3: Updating Excel ###
print("\n📊 Step 3: Updating Top Markets in Excel")
update_excel_with_top_markets()  
print(f"✅ Excel file {EXCEL_FILE_PATH} (Top Markets) has been updated successfully.")

### 🔄 Step 4: Close and Reopen Excel to Refresh Data ###
print("\n🔄 Step 4: Closing and Reopening Excel to Load the Latest Data")
close_excel_script = '''
tell application "Microsoft Excel"
    if it is running then
        quit
    end if
end tell
'''
subprocess.run(["osascript", "-e", close_excel_script])

time.sleep(2)

open_excel_script = f'''
tell application "Microsoft Excel"
    activate
    open POSIX file "{EXCEL_FILE_PATH}"
end tell
'''
subprocess.run(["osascript", "-e", open_excel_script])

### 📸 Step 5: Running Macro to Copy Images & Insert into PowerPoint ###
print("\n📸 Step 5: Running Macro for Top Markets (Slide 3)")
try:
    run_top_markets_macro()
    print("✅ PowerPoint Slide 3 updated successfully!")
except Exception as e:
    print(f"❌ Error running top_markets_macro.py: {e}")

print("\n🎉 **All Steps for Slide 3 Completed Successfully!**")
