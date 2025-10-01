import os
import sys
import subprocess

# Define the base directory
BASE_DIR = os.path.dirname(__file__)

# Define the script paths
SCRIPTS_TO_RUN = [
    "scripts/format/format_sales_data.py",  # ✅ Formats weekly sales data
    "scripts/format/format_spend_data.py",  # ✅ Formats marketing spend data
    "scripts/prepare/prepare_metrics.py",  # ✅ Prepares weekly metrics
    "scripts/prepare/prepare_growth.py",  # ✅ Prepares weekly growth metrics
    "scripts/prepare/prepare_ytd_metrics.py",  # ✅ Prepares YTD metrics
    "scripts/prepare/prepare_ytd_growth.py",  # ✅ Prepares YTD growth metrics
    "scripts/final/finalized_metrics.py",  # ✅ Finalizes weekly metrics
    "scripts/final/finalized_growth.py",  # ✅ Finalizes weekly growth metrics
    "scripts/final/finalized_ytd_metrics.py",  # ✅ Finalizes YTD metrics
    "scripts/final/finalized_ytd_growth.py",  # ✅ Finalizes YTD growth metrics
    "scripts/excel/top_table_excel.py",  # ✅ Updates Excel top table
    "scripts/macros/top_table_macro.py",  # ✅ Runs PowerPoint macro
]

# ✅ Function to run a script and handle errors
def run_script(script_path):
    """Runs a Python script and handles errors gracefully."""
    full_path = os.path.join(BASE_DIR, script_path)
    if os.path.exists(full_path):
        print(f"\n🚀 **Running {script_path}...**")
        try:
            subprocess.run(["python3", full_path], check=True)
            print(f"✅ **{script_path} completed successfully!**")
        except subprocess.CalledProcessError as e:
            print(f"❌ **Error in {script_path}: {e}**")
    else:
        print(f"⚠️ **Skipping {script_path} (not found).**")

# ✅ Execute all scripts in order
for script in SCRIPTS_TO_RUN:
    run_script(script)

print("\n🎉 **Slide 2 Processing Completed Successfully!**")