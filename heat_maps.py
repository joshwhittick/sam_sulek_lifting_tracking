import json
import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

def plot_calendars(data):
    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Split lifts with multiple values separated by semicolons
    df_expanded = df[df['lift'] != 'None'].copy()
    df_expanded['lift'] = df_expanded['lift'].str.split(';')
    df_expanded = df_expanded.explode('lift')

    # Get unique lift types
    unique_lifts = sorted(df_expanded['lift'].unique().tolist())

    lifts = []

    for lift in unique_lifts:
        lift_df = df_expanded[df_expanded['lift'] == lift]
        daily_counts = lift_df.groupby('upload_date').size().reset_index(name='count')

        daily_counts['upload_date'] = pd.to_datetime(daily_counts['upload_date'], format='%d-%m-%Y', errors='coerce')
        daily_counts = daily_counts.dropna(subset=['upload_date'])  # Optional: clean up bad dates


        if daily_counts.empty:
            continue

        daily_counts['dow'] = daily_counts['upload_date'].dt.dayofweek  # Monday=0
        daily_counts['week'] = daily_counts['upload_date'].dt.isocalendar().week

        pivot = daily_counts.pivot_table(index='dow', columns='week', values='count')

        plt.figure(figsize=(15, 6))
        sns.heatmap(pivot, cmap="Greens", linewidths=0.5)
        plt.title(f"{lift} Sessions Heatmap")
        plt.ylabel('Day of Week')
        plt.xlabel('ISO Week Number')
        plt.yticks(ticks=[0, 1, 2, 3, 4, 5, 6], labels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], rotation=0)
        plt.tight_layout()
        lifts.append(plt.gcf())
    
    for fig in lifts:
        st.pyplot(fig)

if __name__ == "__main__":
    file = 'video_data_final.json'
    data = json.load(open(file, 'r'))
    plot_calendars(data)