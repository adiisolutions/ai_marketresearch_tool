import streamlit as st
import requests
import os
import urllib.robotparser
from urllib.parse import urlparse

# --- Config ---
st.set_page_config(page_title="Market Research Tool", layout="wide")
st.title("AI Market Research Summary Tool with robots.txt Compliance")

# --- API Key Setup ---
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))
if not OPENROUTER_API_KEY:
    st.error("OpenRouter API key is missing. Set it in Streamlit secrets or environment variables.")
    st.stop()

# --- robots.txt check function ---
def can_scrape(url, user_agent='MarketResearchBot'):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(base_url + "/robots.txt")
    try:
        rp.read()
        return rp.can_fetch(user_agent, url)
    except:
        return False  # Be cautious if robots.txt not reachable

# --- Input section ---
st.markdown("### Step 1: Enter the website URL to scrape or paste content manually")

url = st.text_input("Website URL (optional, for scraping):")

manual_text = ""
content_to_summarize = ""

if url:
    if can_scrape(url):
        st.success(f"Scraping is allowed by robots.txt on {url}")
        # Here you would scrape the website content
        # For demo, let's just show a placeholder
        st.info("Scraping website content... (Replace with actual scraping code)")
        # Example: content_to_summarize = your_scrape_function(url)
        # For now, ask user to paste scraped text manually:
        manual_text = st.text_area("Paste scraped content here:", height=200)
    else:
        st.error("Scraping disallowed by robots.txt for this URL. Please paste content manually below.")
        manual_text = st.text_area("Paste market content manually here:", height=300)
else:
    manual_text = st.text_area("Paste market content manually here:", height=300)

content_to_summarize = manual_text.strip()

# --- Summary length selection ---
st.markdown("### Step 2: Choose summary length")

summary_length = st.selectbox(
    "Select a summary style:",
    options=[
        "300 words – Quick overview",
        "500–800 words – Detailed summary",
        "1500+ words – In-depth market insight",
        "Custom word limit"
    ]
)

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

# --- Generate summary ---
if st.button("Generate AI Summary"):
    if not content_to_summarize:
        st.warning("Please provide content by scraping or pasting text.")
    else:
        with st.spinner("Generating summary... please wait"):
            prompt = f"Summarize the following market content in about {final_word_limit} words. " \
                     f"If the content is short, expand it with relevant insights to make a detailed and clear summary:\n\n{content_to_summarize}"

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "openrouter/mistral",  # change model as needed
                "messages": [
                    {"role": "system", "content": "You are a professional market research analyst."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000  # adjust if needed based on your quota
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
