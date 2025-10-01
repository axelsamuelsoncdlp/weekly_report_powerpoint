import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set Seaborn style for a clean, professional look
sns.set_theme(style="white")

# Define file paths
BASE_DIR = "/Users/axelsamuelson/Documents/CDLP_code/weekly_reports/data"
FINAL_DATA_DIR = os.path.join(BASE_DIR, "final")
VISUALS_DIR = os.path.join(BASE_DIR, "visuals")

# Ensure the visuals directory exists
os.makedirs(VISUALS_DIR, exist_ok=True)

# Load the metrics_final.csv file
metrics_file_path = os.path.join(FINAL_DATA_DIR, "metrics_final.csv")
if not os.path.exists(metrics_file_path):
    raise ValueError("metrics_final.csv is missing!")

metrics_df = pd.read_csv(metrics_file_path, index_col=0)

# Ensure we have data
if metrics_df.empty:
    raise ValueError("metrics_final.csv is empty!")

# Convert data to numeric (ignoring errors for non-numeric values)
metrics_df = metrics_df.apply(pd.to_numeric, errors='coerce')

# Format numbers properly
metrics_df = metrics_df.applymap(lambda x: f"({abs(int(x)):,})" if x < 0 else f"{int(x):,}" if not pd.isna(x) else "n/m")

# Create a styled table image with improved design
def generate_table_image(df, filename):
    fig, ax = plt.subplots(figsize=(16, len(df) * 0.6))
    ax.axis("tight")
    ax.axis("off")
    
    # Define colors
    header_color = "#2E3B55"
    row_colors = ["#f1f1f1", "#ffffff"]  # Alternating row colors
    
    # Create the table
    table = ax.table(cellText=df.values,
                      colLabels=df.columns,
                      rowLabels=df.index,
                      cellLoc='center',
                      loc='center',
                      colColours=[header_color] * len(df.columns))
    
    # Apply alternating row colors
    for i in range(len(df)):
        color = row_colors[i % len(row_colors)]
        for j in range(len(df.columns)):
            table[(i + 1, j)].set_facecolor(color)
    
    # Adjust font size and scaling
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.5, 1.5)
    
    # Save the improved table image
    save_path = os.path.join(VISUALS_DIR, filename)
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.close()

# Generate and save the improved table image
generate_table_image(metrics_df, "top_table.png")

print("✅ Table image has been successfully generated and saved in the visuals folder!")
