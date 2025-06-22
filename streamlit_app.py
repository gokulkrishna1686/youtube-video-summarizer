import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from youtube_transcript_api.proxies import GenericProxyConfig
from fpdf import FPDF
import io

st.set_page_config(layout="centered")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

st.title('YouTube Video Summary')


if 'video_link' not in st.session_state:
    st.session_state.video_link = ""
if 'summary_text' not in st.session_state:
    st.session_state.summary_text = ""
if 'show_summary_section' not in st.session_state:
    st.session_state.show_summary_section = False
if 'actual_word_count' not in st.session_state:
    st.session_state.actual_word_count = 0
if 'selected_summary_type_index' not in st.session_state:
    st.session_state.selected_summary_type_index = 0
if 'use_word_limit_state' not in st.session_state:
    st.session_state.use_word_limit_state = False
if 'word_limit_value' not in st.session_state:
    st.session_state.word_limit_value = 200

def reset_app():
    st.session_state.video_link = ""
    st.session_state.summary_text = ""
    st.session_state.show_summary_section = False
    st.session_state.actual_word_count = 0
    st.session_state.selected_summary_type_index = 0
    st.session_state.use_word_limit_state = False
    st.session_state.word_limit_value = 200
    st.rerun()

col1, col2 = st.columns([4, 2])
with col1:
    st.session_state.video_link = st.text_input(
        "YouTube Video Link:",
        value=st.session_state.video_link, 
        placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        key="video_link_input" 
    )

summary_options = [
    "Balanced",
    "Professional",
    "Formal",
    "Casual",
    "Concise",
    "Detailed"
]

with col2:
    summary_type = st.selectbox(
        "Select Summary Type:",
        options=summary_options,
        index=st.session_state.selected_summary_type_index,
        help="Choose the style and focus of the summary.",
        key="summary_type_selectbox",
        on_change=lambda: setattr(st.session_state, 'selected_summary_type_index', summary_options.index(st.session_state.summary_type_selectbox))
    )

use_word_limit = st.checkbox(
    "Set a custom word limit for the summary?",
    value=st.session_state.use_word_limit_state,
    key="word_limit_checkbox",
    on_change=lambda: setattr(st.session_state, 'use_word_limit_state', st.session_state.word_limit_checkbox)
)
word_limit = None

if use_word_limit:
    word_limit = st.number_input(
        "Word Limit:",
        min_value = 50,
        max_value = 1000,
        value = st.session_state.word_limit_value,
        step = 10,
        help="The summary will be generated as close to this word limit as possible.",
        key="word_limit_number_input",
        on_change=lambda: setattr(st.session_state, 'word_limit_value', st.session_state.word_limit_number_input)
    )

def get_transcript(video_link):
    try:
        video_id = video_link.split("v=")[1]
        ampersand_position = video_id.find("&")
        if ampersand_position != -1:
            video_id = video_id[:ampersand_position]
        
        with st.spinner("Fetching transcript..."):
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([item["text"] for item in transcript_list])
        return transcript
    except Exception as e:
        st.error(f"Failed to fetch transcript. Please ensure the link is valid and the video has public English subtitles. Error: {e}")
        return None

def create_pdf(summary_text):
    pdf = FPDF()
    pdf.add_page()

    font_loaded = False
    try:
        pdf.add_font('NotoSans', '', 'NotoSans-Regular.ttf', uni=True)
        pdf.set_font('NotoSans', '', 12)
        font_loaded = True
    except:
        pdf.set_font("Arial", size=12)

    if not font_loaded:
        encoded_summary_text = summary_text.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 10, encoded_summary_text)
    else:
        pdf.multi_cell(0, 10, summary_text)

    pdf_buffer = io.BytesIO()
    pdf.output(dest='S', name=pdf_buffer)
    pdf_bytes = pdf_buffer.getvalue()

    return pdf_bytes

col_buttons1, col_buttons2 = st.columns([0.35, 0.8])

with col_buttons1:
    if st.button("Summarize with Gemini"):
        if not st.session_state.video_link.strip():
            st.warning("Please enter a valid YouTube video link.")
            st.session_state.show_summary_section = False
        elif use_word_limit and word_limit is not None and word_limit <= 20:
            st.warning("Please enter a word limit greater than 20 for a meaningful summary. ⚠️")
            st.session_state.show_summary_section = False
        else:
            transcript = get_transcript(st.session_state.video_link)
            if transcript:
                with st.spinner("Generating summary..."):
                    try:
                        base_prompt = f"Summarize the following YouTube transcript:\n\n{transcript}\n\n"
                        style_instruction = ""
                        length_instruction = ""

                        if summary_type == "Professional":
                            style_instruction = "The summary should be highly professional, objective, and suitable for a business context, focusing on key facts and actionable insights."
                        elif summary_type == "Formal":
                            style_instruction = "The summary should maintain a formal tone, using precise language and avoiding contractions or slang."
                        elif summary_type == "Casual":
                            style_instruction = "Provide a casual and easy-to-read summary, as if explaining it to a friend. Use natural language. You may include common internet slang or emojis where appropriate."
                        elif summary_type == "Concise": 
                            style_instruction = "Focus strictly on the absolute key points and main ideas, ensuring brevity."
                        elif summary_type == "Detailed":
                            style_instruction = "Provide a comprehensive and detailed summary, covering all significant aspects and arguments presented."

                        if use_word_limit and word_limit is not None:
                            length_instruction = f"The summary should be {word_limit} words or less."
                        else:
                            length_instruction = "Ensure the summary is comprehensive but concise."

                        prompt_parts = [base_prompt.strip(), style_instruction.strip(), length_instruction.strip()]
                        full_prompt = " ".join(filter(None, prompt_parts))

                        response = model.generate_content(full_prompt)
                        st.session_state.summary_text = response.text
                        st.session_state.actual_word_count = len(response.text.split())
                        st.session_state.show_summary_section = True

                    except:
                        st.error(f"Error during summarization.")
                        st.session_state.show_summary_section = False
            else:
                st.session_state.show_summary_section = False

with col_buttons2:
    if st.button("Clear / Reset App"):
        reset_app()

if st.session_state.show_summary_section and st.session_state.summary_text:
    st.subheader("Summary:")
    st.markdown(st.session_state.summary_text)
    st.subheader("Download Options:")

    download_col1, download_col2, _ = st.columns([0.2, 0.2, 0.6])

    with download_col1:
        st.download_button(
            label="Download as .txt!",
            data=st.session_state.summary_text,
            file_name="video_summary.txt",
            mime="text/plain",
            key="download_txt_button"
        )

    with download_col2:
        pdf_data = create_pdf(st.session_state.summary_text)
        st.download_button(
            label="Download as .pdf!",
            data=pdf_data,
            file_name="video_summary.pdf",
            mime="application/pdf",
            key="download_pdf_button"
        )