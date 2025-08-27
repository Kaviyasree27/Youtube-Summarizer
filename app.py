import streamlit as st
from dotenv import load_dotenv
import os
import re
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Configure the page
st.set_page_config(
    page_title="YouTube Transcript Summarizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load environment variables (Google API Key from .env or Streamlit Secrets)
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt template for Gemini summarizer
prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary points
within 600 words. Please provide the summary of the text given here: """

def extract_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    match = re.search(r"(v=|\/)([A-Za-z0-9_-]{11})", url)
    return match.group(2) if match else None

def extract_transcript_details(youtube_video_url):
    """Fetches transcript text for a given YouTube video URL using the safe static method."""
    video_id = extract_video_id(youtube_video_url)
    if not video_id:
        st.sidebar.warning("Please enter a valid YouTube URL.")
        return None
    try:
        # Use the static method (works reliably for deployed apps)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([entry['text'] for entry in transcript_list])
        return transcript
    except Exception as e:
        st.sidebar.error(f"Error fetching transcript: {e}")
        return None

def generate_gemini_content(transcript_text, prompt):
    """Uses Gemini to generate a summary for the transcript text."""
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Apply your custom dark theme styling (optional)
st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #121212;
        color: #E0E0E0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .sidebar .sidebar-content {
        background-color: #0D47A1;
        color: #D1D1D1;
    }
    button {
        background-color: #0D47A1 !important;
        color: white !important;
        font-weight: 600;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 6px rgba(13,71,161,0.4);
        transition: background-color 0.3s ease;
    }
    button:hover {
        background-color: #0D47A1 !important;
        color: white !important;
        cursor: pointer;
    }
    .stTextInput>div>input {
        border-radius: 8px;
        border: 1.5px solid #0D47A1;
        background-color: #2C2C2C;
        color: #E0E0E0;
        padding: 8px;
        font-size: 16px;
    }
    .stTextInput>div>input:focus {
        outline: none;
        border-color: #1976D2;
        box-shadow: 0 0 4px #1976D2;
    }
    h1, h2 {
        color: #FFFCFB;
        font-weight: 700;
    }
    .stWarning, .stError {
        background-color: #4A148C;
        color: #F3E5F5;
        padding: 10px;
        border-radius: 8px;
    }
    a {
        color: #64B5F6;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar input
st.sidebar.header("YouTube Transcript Summarizer")
youtube_link = st.sidebar.text_input("Enter YouTube Video Link:")

# Main section
st.title("📄 YouTube Transcript to Detailed Notes Converter")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(
            f"http://img.youtube.com/vi/{video_id}/0.jpg",
            width=480,
            use_column_width=False,
        )
    else:
        st.warning("Please enter a valid YouTube URL.")
        video_id = None
else:
    video_id = None

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Get Detailed Notes"):
        if youtube_link and video_id:
            with st.spinner("Fetching transcript and generating summary..."):
                transcript_text = extract_transcript_details(youtube_link)
                if transcript_text:
                    summary = generate_gemini_content(transcript_text, prompt)
                    st.markdown("## 📝 Detailed Notes:")
                    st.write(summary)
                else:
                    st.warning("Transcript could not be retrieved.")
        else:
            st.warning("Please enter a valid YouTube video link.")

st.markdown(
    """
    <hr>
    <p style='font-size: 0.85em; color: #B0BEC5; text-align:center;'>
    Developed by <a href="https://www.linkedin.com/in/kaviya-sree-2a9915290/" target="_blank">Kaviya Sree</a> | Built with Streamlit & Google Gemini
    </p>
    """,
    unsafe_allow_html=True,
)
