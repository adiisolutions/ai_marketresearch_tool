import streamlit as st
import requests
import os
import pyttsx3
from streamlit_chat import message

# --- Configuration ---
st.set_page_config(page_title="Market Research Tool", layout="wide")
st.title("AI Market Research Summary Tool with Voice and Chatbot")

# --- API Key Setup ---
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))
if not OPENROUTER_API_KEY:
    st.error("OpenRouter API key is missing. Set it in Streamlit secrets or environment variables.")
    st.stop()

# --- Initialize Text-to-Speech Engine ---
tts_engine = pyttsx3.init()

# --- Input Section ---
st.markdown("### Paste market content (or website data) below:")
scraped_text = st.text_area("Input content:", height=200)

# --- Summary Length Selection ---
st.markdown("### Choose summary length:")
summary_length = st.selectbox(
    "Select a summary style:",
    options=[
        "300 words – Quick overview",
        "500–800 words – Detailed summary",
        "1500+ words – In-depth market insight",
        "Custom word limit"
    ]
)

# Word limit logic
if summary_length == "Custom word limit":
    custom_limit = st.number_input("Enter your custom word limit:", min_value=100, max_value=5000, step=50)
    final_word_limit = custom_limit
elif "300" in summary_length:
    final_word_limit = 300
elif "500–800" in summary_length:
    final_word_limit = 650
elif "1500+" in summary_length:
    final_word_limit = 1800
else:
    final_word_limit = 500

st.info(f"Summary will be around **{final_word_limit} words**.")

# --- Token trimming ---
MAX_INPUT_TOKENS = 28000  # Reserve tokens for output
if len(scraped_text) > MAX_INPUT_TOKENS:
    st.warning("Input was too long and has been trimmed to fit the model's context limit.")
    scraped_text = scraped_text[:MAX_INPUT_TOKENS]

summary_result = ""

# --- Generate Summary Button ---
if st.button("Generate AI Summary"):
    if not scraped_text.strip():
        st.warning("Please paste content to summarize.")
    else:
        with st.spinner("Generating summary... please wait"):
            prompt = f"Summarize the following market content in about {final_word_limit} words:\n\n{scraped_text}"

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": "You are a professional market research analyst."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1500
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                summary_result = result["choices"][0]["message"]["content"]
                st.success("Summary generated successfully!")
                st.text_area("AI-Generated Summary:", value=summary_result, height=300)
            else:
                st.error(f"Failed to generate summary. Status: {response.status_code}")
                st.json(response.json())

# --- Voice Output ---
if summary_result:
    if st.button("Listen to Summary"):
        tts_engine.say(summary_result)
        tts_engine.runAndWait()

# --- Simple Chatbot using generated summary context ---
st.markdown("---")
st.markdown("### Ask questions about the summary")

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

def ask_bot(question):
    if not summary_result:
        return "Please generate a summary first."
    prompt = f"""You are an AI assistant. Based on the following market research summary, answer the user's question:\n
Summary:\n{summary_result}\n
Question: {question}\nAnswer:"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        ans = response.json()["choices"][0]["message"]["content"]
        return ans.strip()
    else:
        return f"Error: {response.status_code}"

user_question = st.text_input("Enter your question here:")

if user_question:
    answer = ask_bot(user_question)
    st.session_state.chat_history.append((user_question, answer))

if st.session_state.chat_history:
    for i, (q, a) in enumerate(st.session_state.chat_history):
        message(q, is_user=True, key=f"q_{i}")
        message(a, key=f"a_{i}")

# --- Disclaimer ---
st.markdown("---")
st.markdown("""
### Disclaimer  
This tool uses OpenRouter’s AI and respects model limits (~32,768 tokens max).  
Input text is automatically trimmed if it exceeds allowed length.  
You are responsible for ensuring your use of this tool complies with all applicable laws and website terms.
""")
