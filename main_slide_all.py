import os

# ✅ Get the current directory (weekly_reports folder)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ✅ Define the slide script names (excluding main_slide_1.py which doesn't exist)
SLIDE_SCRIPTS = [f"main_slide_{i}.py" for i in range(2, 12)]

# ✅ Iterate and execute each slide script
for slide_script in SLIDE_SCRIPTS:
    script_path = os.path.join(BASE_DIR, slide_script)  # Full path in weekly_reports folder
    
    print(f"\n🚀 **Executing {slide_script}...**")

    if os.path.exists(script_path):
        os.system(f"python3 {script_path}")
    else:
        print(f"❌ {slide_script} not found. Skipping.")

print("\n🎉 **All Slide Processes Completed Successfully!** 🚀")