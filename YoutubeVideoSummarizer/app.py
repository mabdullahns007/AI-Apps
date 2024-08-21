import streamlit as st
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import TranscriptFormat
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
import os

os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

st.title("YouTube Video Summarizer")


# Input for YouTube URL
youtube_url = st.text_input("Enter YouTube URL:")

# Summary type selection
summary_types = ["Brief Summary", "Detailed Summary", "In-Depth Analysis"]
selected_summary_type = st.selectbox("Select summary type:", summary_types)

# Language selection
languages = ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Japanese", "Chinese", "Korean", "Urdu", "Hindi" ]
selected_language = st.selectbox("Select summary language:", languages)

