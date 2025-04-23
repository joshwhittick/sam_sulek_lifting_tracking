import streamlit as st # type: ignore
from scrape import get_youtube_videos, get_date_for_video
import json
import pandas as pd # type: ignore
from analyse import clean_and_enrich_json, get_current_stats
import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore
from datetime import datetime
import seaborn as sns
from heat_maps import plot_calendars

file = 'video_data_final.json'
data = json.load(open(file, 'r'))

st.set_page_config(page_title="Sam Sulek Lifting Tracking", layout="wide")
st.title("Sam Sulek Lifting Tracking")
channel_url = "https://www.youtube.com/channel/UCAuk798iHprjTtwlClkFxMA"

def make_lifting_piechart(lift_ocurences):

    total_sessions = sum(lift_ocurences.values())
    threshold = total_sessions * 0.025
    main_data = {}
    other_total = 0
    other_lifts = []

    for k, v in lift_ocurences.items():
        if v >= threshold:
            main_data[k] = v
        else:
            other_total += v
            other_lifts.append(f'{k} ({v/total_sessions*100:.2f}%)')


    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(main_data.values(), labels=main_data.keys(), autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    st.pyplot(fig)

    st.subheader('Lifts that make up less than 2.5% of total sessions:')

    col1, col2 = st.columns(2)
    col1_vals = other_lifts[:len(other_lifts)//2]
    col2_vals = other_lifts[len(other_lifts)//2:]

    for c in col1_vals:
        col1.write(c)

    for c in col2_vals: 
        col2.write(c)   

if st.button("Get Most Recent Data"):
    st.write("Checking for new videos...")
    res = get_youtube_videos(channel_url)
    res_new = []

    for r in res:
        if r['video_url'] not in [d['video_url'] for d in data]:
            st.write(f"New video(s) found: {r['title']}")
            date = get_date_for_video(r['video_url'])
            r['upload_date'] = date
            res_new.append(r)

    res_new = clean_and_enrich_json(res_new)

    res_new = res_new[::-1]

    for x in res_new:
        data.insert(0, x)

    if len(res_new) != 0:
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)

    df = pd.DataFrame(data)
    st.write(df)
    st.write("Data is now up to date.")

if st.button("Analyse"):
    event_set, day_set, lift_set, event_lengths, lift_ocurences, event_start_end, overall_lift_ocurences = get_current_stats(data)
    
    st.subheader("Frequency of Each Lift (keeping multiple muscle group days as they are):")
    make_lifting_piechart(lift_ocurences)
    
    st.subheader("Frequency of Each Lift (per muscle group i.e. duplicates removed list of muscle groups constructed and then count of each of those is done):")
    make_lifting_piechart(overall_lift_ocurences)

    st.subheader('Event Durations:')
    for event, length in event_lengths.items():
        start, end = event_start_end.get(event, (None, None))
        if start and end:
            st.write(f"{event}: {length} days ({start.strftime('%d-%m-%Y')} to {end.strftime('%d-%m-%Y')})")
        else:
            st.write(f"{event}: {length} days")
    
    st.subheader("Lifting Calendar Plots:")
    plot_calendars(data)