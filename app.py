import streamlit as st

import os

# Set your Google API key
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]


st.title("YouTube Video Summarizer")
st.write("Please enter a YouTube URL to get started.")
