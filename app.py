import streamlit as st
import requests
import os
import urllib.robotparser
from urllib.parse import urlparse

# --- Configuration ---
st.set_page_config(page_title="Market Research Tool", layout="wide")
st.title("AI Market Research Summary Tool")

# --- API Key Setup ---
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

if not OPENROUTER_API_KEY:
    st.error("OpenRouter API key is missing. Set it in Streamlit secrets or environment variables.")
    st.stop()

# --- Function to check robots.txt ---
def can_scrape(url, user_agent="*"):
    try:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{base_url}/robots.txt")
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        # If robots.txt can't be fetched/read, allow cautiously
        return True

# --- Input Section ---
url_input = st.text_input("Or enter website URL to scrape (optional):")

if url_input.strip():
    if not can_scrape(url_input):
        st.error("Scraping disallowed by the website's robots.txt. Please provide text manually or use another URL.")
        st.stop()
    else:
        try:
            res = requests.get(url_input, timeout=10)
            if res.status_code == 200:
                scraped_text = res.text
            else:
                st.error(f"Failed to fetch the URL. Status code: {res.status_code}")
                st.stop()
        except Exception as e:
            st.error(f"Error fetching the URL: {e}")
            st.stop()
else:
    scraped_text = st.text_area("Paste market content (or website data) below:", height=200)

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

# --- Generate Summary Button ---
if st.button("Generate AI Summary"):
    if not scraped_text.strip():
        st.warning("Please paste content to summarize or enter a valid URL.")
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
            else:
                st.error(f"Failed to generate summary. Status: {response.status_code}")
                st.json(response.json())
