import subprocess
import sys
import os
import time

# Ensure the scripts folder is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Define file path
EXCEL_FILE_PATH = "/Users/axelsamuelson/Documents/CDLP_code/weekly_reports/data/weekly_report.xlsm"

def run_macro():
    """Runs the VBA macro for top_markets in Excel on macOS."""
    
    print(f"🔍 Opening Excel and running macro...")

    applescript = f'''
    tell application "Microsoft Excel"
        activate
        open POSIX file "{EXCEL_FILE_PATH}"
        delay 5
        tell active workbook
            run VB macro "CopyTopMarketsToPowerPoint"
        end tell
        delay 5
        close saving yes
    end tell
    '''
    
    # Run AppleScript to execute the macro
    result = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True)
    
    # Log output and errors
    if result.returncode == 0:
        print("✅ VBA Macro executed successfully!")
    else:
        print(f"❌ Error running VBA Macro: {result.stderr.strip()}")

# Run function only if executed directly
if __name__ == "__main__":
    run_macro()
    time.sleep(2)  # Ensure PowerPoint has time to process
