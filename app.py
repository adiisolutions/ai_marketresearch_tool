import streamlit as st
import requests
import os

# --- Page Config ---
st.set_page_config(page_title="AI Market Research Tool", layout="wide")
st.title("AI Market Research + Chatbot Assistant")

# --- API Key ---
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))
if not OPENROUTER_API_KEY:
    st.error("Missing API Key. Please set it in Streamlit secrets or env variables.")
    st.stop()

# --- Input Section ---
st.markdown("### Paste content (from website or notes):")
scraped_text = st.text_area("Input content", height=200)

# --- Summary Length Selector ---
st.markdown("### Choose summary length:")
summary_length = st.selectbox(
    "Select style:",
    options=[
        "300 words – Quick overview",
        "500–800 words – Detailed summary",
        "1500+ words – In-depth market insight",
        "Custom word limit"
    ]
)

if summary_length == "Custom word limit":
    custom_limit = st.number_input("Custom word limit:", min_value=100, max_value=5000, step=50)
    final_word_limit = custom_limit
elif "300" in summary_length:
    final_word_limit = 300
elif "500–800" in summary_length:
    final_word_limit = 650
else:
    final_word_limit = 1800

st.info(f"Summary will be around **{final_word_limit} words**.")

# --- Summary Generation ---
MAX_INPUT_TOKENS = 28000
if len(scraped_text) > MAX_INPUT_TOKENS:
    st.warning("Text too long, trimmed to fit model.")
    scraped_text = scraped_text[:MAX_INPUT_TOKENS]

if st.button("Generate AI Summary"):
    if not scraped_text.strip():
        st.warning("Please paste some text.")
    else:
        with st.spinner("Generating summary..."):
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            prompt = f"Summarize the following market content in about {final_word_limit} words:\n\n{scraped_text}"

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
                st.success("Summary generated!")
                st.text_area("AI Summary:", value=summary, height=300)
                st.session_state["summary_context"] = summary
            else:
                st.error("Failed to generate summary.")
                st.json(response.json())

# --- Chatbot Assistant ---
st.markdown("---")
st.markdown("### Chatbot Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask the chatbot about your market or company:")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    trimmed_history = st.session_state.chat_history[-10:]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    context = st.session_state.get("summary_context", "")

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": f"You're a helpful assistant. Only use this context for answers:\n\n{context}"}
        ] + trimmed_history,
        "max_tokens": 600
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        reply = result["choices"][0]["message"]["content"].strip()

        # Avoid repeating exact response
        if not any(reply == m["content"] for m in st.session_state.chat_history if m["role"] == "assistant"):
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

# Display conversation
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")

# --- Disclaimer ---
st.markdown("---")
st.markdown("**Disclaimer:** Use responsibly. Follow website terms and legal use of data.")
