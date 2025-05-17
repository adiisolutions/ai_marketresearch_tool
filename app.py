import streamlit as st
import requests
import os

# --- Configuration ---
st.set_page_config(page_title="Market Research Tool", layout="wide")
st.title("AI Market Research Summary Tool")

# --- API Key Setup ---
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

if not OPENROUTER_API_KEY:
    st.error("OpenRouter API key is missing. Set it in Streamlit secrets or environment variables.")
    st.stop()

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

# --- Generate Summary Button ---
if st.button("Generate AI Summary"):
    if not scraped_text.strip():
        st.warning("Please paste content to summarize.")
    else:
        with st.spinner("Generating summary... please wait"):
            prompt = (
                f"Expand and summarize the following market content into about {final_word_limit} words. "
                f"Make it detailed, clear, and useful for business research:\n\n{scraped_text}"
            )

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "anthropic/claude-3-sonnet-20240229",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                summary = result["choices"][0]["message"]["content"]
                st.success("Summary generated successfully!")
                st.text_area("AI-Generated Summary:", value=summary, height=300)
            else:
                st.warning("The input content is short. The AI will try to expand it into a detailed summary.")
                st.error(f"Failed to generate summary. Status: {response.status_code}")
                st.json(response.json())
