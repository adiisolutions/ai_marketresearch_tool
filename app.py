import streamlit as st
import requests
import os

# --- Page Config ---
st.set_page_config(page_title="Market Research Tool", layout="wide")
st.title("AI Market Research Summary Tool")

# --- API Key Setup ---
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

if not OPENROUTER_API_KEY:
    st.error("OpenRouter API key is missing. Set it in Streamlit secrets or environment variables.")
    st.stop()

# --- Input Area ---
st.markdown("### Paste market content or scraped data below:")
scraped_text = st.text_area("Input content:", height=200)  # reduced height for cleaner UI

# --- Summary Length Options ---
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

# --- Word Limit Logic ---
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
            # --- Updated Prompt for Smart Expansion ---
            prompt = f"""
You are a market research analyst.

The content provided below may be short, unstructured, or lacking in detail.
Your task is to expand and convert it into a professional, easy-to-read market research summary of approximately {final_word_limit} words.

Your summary should include:
- Key market points and insights
- Trends or patterns (even if inferred)
- Possible business implications
- Actionable advice or recommendations
- Well-structured sections with headings

If details are missing, intelligently elaborate based on common market knowledge. Do NOT fabricate fake statistics, but it's okay to generalize.

Here is the raw input:

\"\"\"{scraped_text}\"\"\"
"""

            # --- API Request ---
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "openrouter/openai/gpt-3.5-turbo",  # Replace with a valid model ID if needed
                "messages": [
                    {"role": "system", "content": "You are a helpful and knowledgeable market research expert."},
                    {"role": "user", "content": prompt}
                ]
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

            # --- Handle Response ---
            if response.status_code == 200:
                result = response.json()
                summary = result["choices"][0]["message"]["content"]
                st.success("Summary generated successfully!")
                st.text_area("AI-Generated Summary:", value=summary, height=400)
            else:
                st.error(f"Failed to generate summary. Status: {response.status_code}")
                st.json(response.json())
