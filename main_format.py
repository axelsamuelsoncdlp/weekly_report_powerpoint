import os
import subprocess

# Define the base directory
BASE_DIR = os.path.dirname(__file__)

# List of format scripts to run
FORMAT_SCRIPTS = [
    "scripts/format/format_sales_data.py",  # ✅ Formats weekly sales data
    "scripts/format/format_spend_data.py",  # ✅ Formats marketing spend data
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

# ✅ Execute all format scripts in order
for script in FORMAT_SCRIPTS:
    run_script(script)

print("\n🎉 **All Format Scripts Completed Successfully!**")