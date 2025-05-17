import streamlit as st
import requests
import os
from bs4 import BeautifulSoup

# --- Configuration ---
st.set_page_config(page_title="Market Research Tool", layout="centered")
st.title("AI Market Research Summary Tool")

# --- API Key ---
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))
if not OPENROUTER_API_KEY:
    st.error("API key missing. Set it in Streamlit secrets or environment variables.")
    st.stop()

# --- Layout: Side-by-side Inputs ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Option 1: Enter website URL**")
    url_input = st.text_input("Website URL (e.g. https://example.com)", label_visibility="collapsed")

with col2:
    st.markdown("**Option 2: Paste content manually**")
    scraped_text = st.text_area("Paste Content Here", height=150, label_visibility="collapsed")

# --- Summary Options ---
st.markdown("### Summary Length")
summary_length = st.selectbox(
    "Choose summary length:",
    options=[
        "300 words – Quick overview",
        "500–800 words – Detailed summary",
        "1500+ words – In-depth market insight",
        "Custom word limit"
    ]
)

if summary_length == "Custom word limit":
    custom_limit = st.number_input("Enter custom word limit:", min_value=100, max_value=5000, step=50)
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

# --- Scrape Function ---
def scrape_website(url):
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all(["p", "h1", "h2", "h3", "li"])
        text = "\n".join(p.get_text() for p in paragraphs)
        return text.strip()
    except Exception as e:
        return f"Error scraping site: {e}"

# --- Summary Button ---
if st.button("Generate AI Summary", use_container_width=True):
    content_to_summarize = scraped_text

    if url_input:
        with st.spinner("Scraping website content..."):
            scraped = scrape_website(url_input)
            if scraped.startswith("Error scraping site:"):
                st.error(scraped)
                st.stop()
            elif len(scraped.strip()) < 100:
                st.warning("The website content seems too short or empty. Try a different URL or paste text manually.")
                st.stop()
            else:
                content_to_summarize = scraped

    if not content_to_summarize.strip():
        st.warning("No content to summarize. Please paste text or enter a valid URL.")
    else:
        with st.spinner("Generating summary..."):
            prompt = f"Summarize the following market content in about {final_word_limit} words:\n\n{content_to_summarize}"

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a professional market research analyst."},
                    {"role": "user", "content": prompt}
                ]
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                summary = result["choices"][0]["message"]["content"]
                st.toast("Summary ready!", icon="✅")
                st.text_area("AI-Generated Summary", value=summary, height=300)
            else:
                st.error(f"Failed to generate summary. Status: {response.status_code}")
                st.json(response.json())
