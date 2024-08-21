import streamlit as st

import os

# Set your Google API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyCqMCBk2k1-pbACD3grHQIpiK7NKiDEx4A"

st.title("YouTube Video Summarizer")

# Input for YouTube URL
youtube_url = st.text_input("Enter YouTube URL:")

# Summary type selection
summary_types = ["Brief Summary", "Detailed Summary", "In-Depth Analysis"]
selected_summary_type = st.selectbox("Select summary type:", summary_types)

# Language selection
languages = ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Japanese", "Chinese", "Korean", "Urdu" , "Hindi" ]
selected_language = st.selectbox("Select summary language:", languages)
