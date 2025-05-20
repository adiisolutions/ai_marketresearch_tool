import streamlit as st
import requests
import os
from gtts import gTTS
import base64

# --- Configuration ---
st.set_page_config(page_title="Market Research Tool", layout="wide")
st.title("AI Market Research Summary Tool")

# --- API Key Setup ---
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

if not OPENROUTER_API_KEY:
    st.error("OpenRouter API key is missing. Set it in Streamlit secrets or environment variables.")
    st.stop()

# --- Text-to-Speech helper ---
def text_to_audio(text):
    tts = gTTS(text=text, lang='en')
    tts.save("summary.mp3")
    with open("summary.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
    <audio controls>
      <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3" />
    </audio>
    """
    return audio_html

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

# --- Max Token Handling ---
MAX_INPUT_TOKENS = 28000  # Reserve 1,500 for output approx
if len(scraped_text) > MAX_INPUT_TOKENS:
    st.warning(f"Input was too long and has been automatically trimmed to fit the model's context limit.")
    scraped_text = scraped_text[:MAX_INPUT_TOKENS]

summary = None  # Initialize summary variable

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
                summary = result["choices"][0]["message"]["content"]
                st.success("Summary generated successfully!")
                st.text_area("AI-Generated Summary:", value=summary, height=300)

                # --- Voice Playback ---
                st.markdown("### Listen to the summary:")
                audio_html = text_to_audio(summary)
                st.markdown(audio_html, unsafe_allow_html=True)

            else:
                st.error(f"Failed to generate summary. Status: {response.status_code}")
                st.json(response.json())

# --- Chatbot Q&A Section ---
if summary:
    st.markdown("---")
    st.markdown("### Ask questions about the market data")

    question = st.text_input("Enter your question:")

    if question:
        with st.spinner("Getting answer..."):
            chat_prompt = f"You are a market research expert. Based on this data:\n{summary}\nAnswer this question:\n{question}"

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": "You are a helpful market research assistant."},
                    {"role": "user", "content": chat_prompt}
                ],
                "max_tokens": 500
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            if response.status_code == 200:
                answer = response.json()["choices"][0]["message"]["content"]
                st.markdown("**Answer:**")
                st.write(answer)
            else:
                st.error(f"Failed to get answer. Status: {response.status_code}")

# --- Disclaimer ---
st.markdown("---")
st.markdown("""
### Disclaimer  
This tool uses OpenRouter’s AI and respects model limits (~32,768 tokens max).  
Input text is automatically trimmed if it exceeds allowed length.  
You are responsible for ensuring your use of this tool complies with all applicable laws and website terms.
""")
