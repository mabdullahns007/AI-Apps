import streamlit as st

import os

# Set your Google API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyCqMCBk2k1-pbACD3grHQIpiK7NKiDEx4A"

st.title("YouTube Video Summarizer")
st.write("Please enter a YouTube URL to get started.")
