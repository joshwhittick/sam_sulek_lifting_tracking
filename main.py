import streamlit as st # type: ignore
from scrape import get_youtube_videos, get_youtube_videos_v2, get_youtube_videos_v3

st.set_page_config(page_title="Sam Sulek Lifting Tracking", layout="wide")
st.title("Sam Sulek Lifting Tracking")
channel_url = "https://www.youtube.com/channel/UCAuk798iHprjTtwlClkFxMA"

if st.button("Scrape Data"):
    st.write(get_youtube_videos(channel_url))
    st.write(get_youtube_videos_v2(channel_url))
    st.write(get_youtube_videos_v3(channel_url))