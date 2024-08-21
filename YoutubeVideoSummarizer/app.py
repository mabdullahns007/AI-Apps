import streamlit as st
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import TranscriptFormat
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
import os

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


if youtube_url:
    try:
        # Load YouTube transcript
        loader = YoutubeLoader.from_youtube_url(
            youtube_url,
            add_video_info=True,
            transcript_format=TranscriptFormat.CHUNKS,
            chunk_size_seconds=180,
        )
        
        docs = loader.load()
        
        # Display video title
        st.subheader(f"Video Title: {docs[0].metadata['title']}")
        
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True,
                                     temperature=0.7)
        
        # Define prompts with language selection

        #STUFF
        stuff_prompt = """

        Write a brief summary of the following text in {language} with the following guidelines:

        Introduction: Begin with a brief introduction that outlines the main topic.
        Key Points: List the key points. Use bullet points for clarity.
        Conclusion: End with a concluding statement that encapsulates overall message or takeaway.
        Tone: Maintain a clear and neutral tone, suitable for a broad audience.

        Text:
        ```{text}```
        """
        stuff_prompt_template = PromptTemplate(template=stuff_prompt, input_variables=["text", "language"])

        #MAP_REDUCE
        map_prompt = """
        Write a detailed summary of the following:
        "{text}"
        1. Key Points: List the key points covered in this section using bullet points.
        2. Details: Provide a detailed explanation of each key point.

        DETAILED SUMMARY:
        """
        map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])


        combine_prompt = """

        The following is set of summaries:
        ```{text}```
        Take these and distill it into a final, consolidated summary.
        Write the summary in {language} with the following guidelines:
        
        Introduction: Begin with a brief introduction that outlines the main topic.
        Key Points: List the key points. Use bullet points for clarity.
        Details: Offer a detailed explanation of each key point. Ensure the information is easy to read and well-organized.
        Conclusion: End with a concluding statement that encapsulates overall message or takeaway.
        Formatting: Use main heading and sub headings, bullet points, and short paragraphs to make the summary easy to scan and understand.
        Tone: Maintain a clear and neutral tone, suitable for a broad audience.
        
        """
        combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text", "language"])

        #REFINE
        question_prompt = """
        Write a concise summary of the following:
        {text}
        CONCISE SUMMARY:

        """
        question_prompt_template = PromptTemplate(template=question_prompt, input_variables=["text"])

        refine_prompt = """
        Your job is to produce a final summary with the following guidelines:

        Introduction: Begin with a brief introduction that outlines the main topic.
        Key Points: List the key points. Use bullet points for clarity.
        Details: Offer a detailed explanation of each key point. Ensure the information is easy to read and well-organized.
        Conclusion: End with a concluding statement that encapsulates overall message or takeaway.
        Formatting: Use headings, bullet points, and short paragraphs to make the summary easy to scan and understand.
        Tone: Maintain a clear and neutral tone, suitable for a broad audience.

        We have provided an existing summary up to a certain point: {existing_answer}
        We have the opportunity to refine the existing summary (only if needed) with some more context below.
        ------------
        {text}
        ------------
        Given the new context, refine the original summary.
        If the context isn't useful, return the original summary.
        IN-DEPTH ANALYSIS SUMMARY IN {language}:
        """
        refine_prompt_template = PromptTemplate(template=refine_prompt, input_variables=["existing_answer", "text", "language"])


        # Create summary chain based on selected type
        if selected_summary_type == "Brief Summary":
            summary_chain = load_summarize_chain(llm=llm,
                                                 chain_type='stuff',
                                                 prompt=stuff_prompt_template,
                                                 verbose=False)
        elif selected_summary_type == "Detailed Summary":
            summary_chain = load_summarize_chain(llm=llm,
                                                 chain_type='map_reduce',
                                                 map_prompt=map_prompt_template,
                                                 combine_prompt=combine_prompt_template,
                                                 verbose=False)
        else:  # refine
            summary_chain = load_summarize_chain(llm=llm,
                                                 chain_type='refine',
                                                 question_prompt=question_prompt_template,
                                                 refine_prompt=refine_prompt_template,
                                                 verbose=False)
        
        
        # Run the summarization
        with st.spinner(f"Generating {selected_summary_type} summary in {selected_language}..."):
            summary = summary_chain.run({"input_documents": docs, "language": selected_language})
        
        # Display the summary
        st.subheader(f"Video Summary ({selected_summary_type}) in {selected_language}:")
        st.write(summary)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    st.write("Please enter a YouTube URL to get started.")

