import streamlit as st
import requests
import os
import pyttsx3
import time
from streamlit_chat import message
from typing import List, Tuple, Optional
from dataclasses import dataclass
import base64
from io import BytesIO
from PIL import Image
import json

# --- Constants and Configuration ---
MAX_INPUT_TOKENS = 28000  # Reserve tokens for output
TTS_VOICE_OPTIONS = {
    'Male': 0,
    'Female': 1
}
MODELS = {
    'Mistral 7B': 'mistralai/mistral-7b-instruct',
    'GPT-4': 'openai/gpt-4',
    'Claude 2': 'anthropic/claude-2'
}

# --- Data Classes ---
@dataclass
class SummaryConfig:
    length: int
    style: str
    include_key_points: bool
    include_statistics: bool

# --- Page Configuration ---
st.set_page_config(
    page_title="Advanced Market Research AI",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stTextArea textarea {
        min-height: 300px;
    }
    .summary-box {
        border-radius: 10px;
        padding: 20px;
        background-color: #f9f9f9;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 15px;
        border-radius: 10px;
        background-color: #f0f2f6;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 24px;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'summary_result' not in st.session_state:
    st.session_state.summary_result = ""
if 'last_question' not in st.session_state:
    st.session_state.last_question = ""
if 'api_calls' not in st.session_state:
    st.session_state.api_calls = 0

# --- Sidebar Configuration ---
with st.sidebar:
    st.title("⚙️ Settings")
    
    # API Key Configuration
    OPENROUTER_API_KEY = st.text_input(
        "OpenRouter API Key",
        type="password",
        value=st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
    )
    
    if not OPENROUTER_API_KEY:
        st.error("API key is required to proceed")
        st.stop()
    
    # Model Selection
    selected_model = st.selectbox(
        "AI Model",
        options=list(MODELS.keys()),
        index=0,
        help="Select the AI model for analysis. More advanced models may cost more."
    )
    
    # TTS Configuration
    st.subheader("Voice Settings")
    tts_voice = st.selectbox(
        "Voice Gender",
        options=list(TTS_VOICE_OPTIONS.keys()),
        index=0
    )
    tts_rate = st.slider("Speech Rate", 100, 200, 150)
    
    # Advanced Options
    with st.expander("Advanced Options"):
        max_tokens = st.number_input(
            "Max Response Tokens",
            min_value=100,
            max_value=4000,
            value=1500,
            step=100
        )
        temperature = st.slider(
            "Creativity (Temperature)",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1
        )

# --- Main App ---
st.title("📊 Advanced AI Market Research Tool")
st.markdown("""
This tool helps you analyze market research content with AI-powered summarization, insights, and interactive Q&A.
""")

# --- Input Section ---
with st.expander("📥 Input Content", expanded=True):
    input_method = st.radio(
        "Input Method",
        options=["Paste Text", "URL (Coming Soon)"],
        horizontal=True
    )
    
    if input_method == "Paste Text":
        scraped_text = st.text_area(
            "Market Research Content",
            placeholder="Paste your market research content, article, or report here...",
            height=300,
            help="For best results, provide at least 500 words of content."
        )
    else:
        scraped_text = ""
        st.warning("URL input feature is coming soon!")

# --- Summary Configuration ---
with st.expander("⚙️ Summary Configuration"):
    col1, col2 = st.columns(2)
    
    with col1:
        summary_length = st.selectbox(
            "Summary Length",
            options=[
                "300 words – Executive Summary",
                "500–800 words – Detailed Analysis",
                "1500+ words – Comprehensive Report",
                "Custom length"
            ],
            index=1
        )
        
        if summary_length == "Custom length":
            custom_limit = st.number_input(
                "Custom Word Limit",
                min_value=100,
                max_value=5000,
                step=50,
                value=800
            )
            final_word_limit = custom_limit
        elif "300" in summary_length:
            final_word_limit = 300
        elif "500–800" in summary_length:
            final_word_limit = 650
        elif "1500+" in summary_length:
            final_word_limit = 1800
        else:
            final_word_limit = 500
    
    with col2:
        st.markdown("**Summary Features**")
        include_key_points = st.checkbox("Include Key Points", value=True)
        include_statistics = st.checkbox("Highlight Statistics", value=True)
        include_trends = st.checkbox("Identify Trends", value=True)

# --- Token Management ---
if scraped_text and len(scraped_text) > MAX_INPUT_TOKENS:
    scraped_text = scraped_text[:MAX_INPUT_TOKENS]
    st.warning(f"Input was too long and has been trimmed to {MAX_INPUT_TOKENS} characters.")

# --- AI Processing Functions ---
def generate_summary(
    text: str, 
    word_limit: int, 
    model: str, 
    include_key_points: bool = True,
    include_statistics: bool = True
) -> Optional[str]:
    """Generate an AI-powered market research summary."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://market-research-tool.streamlit.app",
        "X-Title": "Market Research AI Tool"
    }
    
    features = []
    if include_key_points:
        features.append("key bullet points")
    if include_statistics:
        features.append("notable statistics")
    
    features_text = " including " + ", ".join(features) if features else ""
    
    prompt = f"""As a senior market research analyst, create a {word_limit}-word summary of the following content{features_text}:
    
Content:
{text}

Summary Guidelines:
- Use professional business language
- Highlight key market trends and insights
- Maintain an objective, data-driven tone
- Structure the summary logically
- Include relevant data points when available"""

    payload = {
        "model": MODELS[model],
        "messages": [
            {"role": "system", "content": "You are a top-tier market research analyst with 20+ years of experience."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        st.session_state.api_calls += 1
        
        if response.status_code == 200:
            result = response.json()
            elapsed = time.time() - start_time
            st.success(f"Analysis completed in {elapsed:.1f} seconds")
            return result["choices"][0]["message"]["content"]
        else:
            st.error(f"API Error: {response.status_code}")
            st.json(response.json())
            return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

def ask_ai(question: str, context: str) -> str:
    """Ask a question about the generated summary."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""You are a market research expert. Answer the question based on the following analysis:
    
Market Research Analysis:
{context}

Question: {question}

Answer Guidelines:
- Be precise and professional
- Reference specific parts of the analysis when possible
- If the question can't be answered from the analysis, say so
- Keep answers concise but thorough"""

    payload = {
        "model": MODELS[selected_model],
        "messages": [
            {"role": "system", "content": "You are a helpful market research assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 800,
        "temperature": 0.5
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        st.session_state.api_calls += 1
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Error: API request failed with status {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# --- Text-to-Speech Function ---
def text_to_speech(text: str, voice: str, rate: int = 150):
    """Convert text to speech with configurable voice and speed."""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[TTS_VOICE_OPTIONS[voice]].id)
        engine.setProperty('rate', rate)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")

# --- Generate Summary Action ---
if st.button("🚀 Generate Market Analysis", use_container_width=True):
    if not scraped_text.strip():
        st.warning("Please input content to analyze")
    else:
        with st.spinner("🧠 Analyzing content with AI..."):
            summary = generate_summary(
                scraped_text,
                final_word_limit,
                selected_model,
                include_key_points,
                include_statistics
            )
            
            if summary:
                st.session_state.summary_result = summary
                st.session_state.chat_history = []

# --- Display Results ---
if st.session_state.summary_result:
    st.markdown("---")
    st.markdown("## 📝 Market Research Summary")
    
    with st.container():
        st.markdown(f'<div class="summary-box">{st.session_state.summary_result}</div>', unsafe_allow_html=True)
        
        # Export Options
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔊 Listen to Summary", use_container_width=True):
                text_to_speech(st.session_state.summary_result, tts_voice, tts_rate)
        with col2:
            st.download_button(
                label="📄 Download as TXT",
                data=st.session_state.summary_result,
                file_name="market_research_summary.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col3:
            st.download_button(
                label="📊 Download as JSON",
                data=json.dumps({"summary": st.session_state.summary_result}),
                file_name="market_research_summary.json",
                mime="application/json",
                use_container_width=True
            )

# --- Chat Interface ---
st.markdown("---")
st.markdown("## 💬 Ask About This Analysis")

if st.session_state.summary_result:
    chat_container = st.container()
    
    with st.form(key="chat_form"):
        user_question = st.text_input(
            "Your question about this analysis:",
            placeholder="What are the key trends in this market?",
            key="user_question"
        )
        
        submitted = st.form_submit_button("Ask", use_container_width=True)
        
        if submitted and user_question:
            with st.spinner("Thinking..."):
                answer = ask_ai(user_question, st.session_state.summary_result)
                st.session_state.chat_history.append((user_question, answer))
                st.session_state.last_question = user_question
    
    # Display chat history
    if st.session_state.chat_history:
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for i, (q, a) in enumerate(st.session_state.chat_history):
                message(q, is_user=True, key=f"user_{i}")
                message(a, key=f"ai_{i}")
            st.markdown('</div>', unsafe_allow_html=True)

# --- Analytics ---
with st.expander("📈 Usage Analytics"):
    st.write(f"API Calls: {st.session_state.api_calls}")
    if st.session_state.summary_result:
        st.write(f"Summary Length: {len(st.session_state.summary_result.split())} words")
    if st.session_state.chat_history:
        st.write(f"Chat Questions: {len(st.session_state.chat_history)}")

# --- Footer ---
st.markdown("---")
st.markdown("""
### About This Tool
This advanced market research tool uses cutting-edge AI to analyze and summarize complex market data. 
It's designed for professionals who need quick, accurate insights from large volumes of information.

**Key Features:**
- AI-powered market analysis
- Configurable summary depth and style
- Interactive Q&A about your research
- Voice output for hands-free use
- Export options for further analysis

*Note: This tool uses OpenRouter's API to access various AI models. Usage may be subject to API limits and costs.*
""")
