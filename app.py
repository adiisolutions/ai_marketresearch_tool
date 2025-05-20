import streamlit as st
import requests
import os
import pyttsx3
from streamlit_chat import message

--- Configuration ---

st.set_page_config(page_title="Market Research Tool", layout="wide") st.title("AI Market Research Summary Tool")

--- API Key Setup ---

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

if not OPENROUTER_API_KEY: st.error("OpenRouter API key is missing. Set it in Streamlit secrets or environment variables.") st.stop()

--- Input Section ---

st.markdown("### Paste market content (or website data) below:") scraped_text = st.text_area("Input content:", height=200)

--- Summary Length Selection ---

st.markdown("### Choose summary length:") summary_length = st.selectbox( "Select a summary style:", options=[ "300 words – Quick overview", "500–800 words – Detailed summary", "1500+ words – In-depth market insight", "Custom word limit" ] )

Word limit logic

if summary_length == "Custom word limit": custom_limit = st.number_input("Enter your custom word limit:", min_value=100, max_value=5000, step=50) final_word_limit = custom_limit elif "300" in summary_length: final_word_limit = 300 elif "500–800" in summary_length: final_word_limit = 650 elif "1500+" in summary_length: final_word_limit = 1800 else: final_word_limit = 500

st.info(f"Summary will be around {final_word_limit} words.")

--- Max Token Handling ---

MAX_INPUT_TOKENS = 28000  # Reserve 1,500 for output if len(scraped_text) > MAX_INPUT_TOKENS: st.warning(f"Input was too long and has been automatically trimmed to fit the model's context limit.") scraped_text = scraped_text[:MAX_INPUT_TOKENS]

--- Generate Summary Button ---

if st.button("Generate AI Summary"): if not scraped_text.strip(): st.warning("Please paste content to summarize.") else: with st.spinner("Generating summary... please wait"): prompt = f"Summarize the following market content in about {final_word_limit} words:\n\n{scraped_text}"

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

            # Voice Output
            if st.button("Play Summary Audio"):
                engine = pyttsx3.init()
                engine.say(summary)
                engine.runAndWait()
        else:
            st.error(f"Failed to generate summary. Status: {response.status_code}")
            st.json(response.json())

--- Chatbot ---

st.markdown("---") st.markdown("### Ask Questions About the Content") if scraped_text: user_question = st.text_input("Ask a question about the pasted content:") if user_question: chatbot_prompt = f"Based on this content, answer the question clearly:\n\nCONTENT:\n{scraped_text}\n\nQUESTION:\n{user_question}"

headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are an assistant that answers based on provided market research."},
            {"role": "user", "content": chatbot_prompt}
        ],
        "max_tokens": 1000
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        message(user_question, is_user=True)
        message(reply)
    else:
        st.error("Failed to fetch chatbot response.")

--- Disclaimer ---

st.markdown("---") st.markdown("""

Disclaimer

This tool uses OpenRouter’s AI and respects model limits (~32,768 tokens max).
Input text is automatically trimmed if it exceeds allowed length.
You are responsible for ensuring your use of this tool complies with all applicable laws and website terms. """)

