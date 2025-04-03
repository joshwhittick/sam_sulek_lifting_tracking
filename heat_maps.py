import json
import pandas as pd
import matplotlib.pyplot as plt
import calmap
from datetime import datetime

# --- Load and Prepare Data ---
with open('video_data_final.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)
# Convert upload_date to datetime (assumed format: dd-mm-YYYY)
df['date'] = pd.to_datetime(df['upload_date'], format='%d-%m-%Y', errors='coerce')
df = df.dropna(subset=['date'])

# --- Overall Sessions ---
overall_series = df.groupby('date').size()

# --- Top 7 Lifts ---
df_valid = df[df['lift'] != 'None']
top7_lifts = df_valid['lift'].value_counts().head(7).index.tolist()

# Create a dictionary to hold the date-count series for each lift type
lift_series = {}
for lift in top7_lifts:
    s = df_valid[df_valid['lift'] == lift].groupby('date').size()
    lift_series[lift] = s

# --- Plotting using calmap in Subplots ---
# Create a figure with 4 rows and 2 columns (total 8 subplots)
fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(20, 20))
axes = axes.flatten()

# Plot overall sessions heatmap in the first subplot.
plt.sca(axes[0])
calmap.calendarplot(overall_series, fillcolor='lightgray', cmap='Greens')
axes[0].set_title("Overall Lifting Sessions")

# Plot each of the top 7 lift types in its own subplot.
for i, lift in enumerate(top7_lifts):
    plt.sca(axes[i + 1])
    calmap.calendarplot(lift_series[lift], fillcolor='lightgray', cmap='Greens')
    axes[i + 1].set_title(f"{lift} Sessions")

plt.tight_layout()
plt.show()
