import streamlit as st
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

# ---- Setup ----
st.set_page_config(page_title="Market Research Tool", layout="centered")
st.title("AI Market Research + Chatbot")

# ---- Session State Init ----
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = False

# ---- Scrape & Summarize ----
@st.cache_data(show_spinner=True)
def scrape_and_summarize(url, word_limit):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        content = ' '.join([p.text for p in soup.find_all('p')])
        content = content[:6000]

        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
        summary = summarizer(content, max_length=word_limit, min_length=100, do_sample=False)[0]['summary_text']
        return summary
    except Exception as e:
        return f"Error: {e}"

# ---- Sidebar for Input ----
with st.sidebar:
    st.header("Market Research Tool")
    url = st.text_input("Enter Website URL")
    length = st.selectbox("Summary Length", ["Short (~300 words)", "Detailed (1500+ words)"])
    word_limit = 300 if "300" in length else 1024
    if st.button("Generate Summary"):
        if url:
            with st.spinner("Summarizing..."):
                st.session_state.summary = scrape_and_summarize(url, word_limit)
                st.session_state.messages = []  # Clear old chat
                st.success("Summary Ready!")

# ---- Show Summary ----
if st.session_state.summary:
    st.subheader("Summary")
    st.write(st.session_state.summary)

# ---- Chatbot Toggle ----
if st.session_state.summary and st.button("Toggle Chatbot"):
    st.session_state.chatbot = not st.session_state.chatbot

# ---- Chatbot Interface ----
if st.session_state.chatbot:
    st.markdown("---")
    st.subheader("Ask the Chatbot About This Website")

    for msg in st.session_state.messages:
        role = "You" if msg["role"] == "user" else "Bot"
        st.markdown(f"**{role}:** {msg['content']}")

    user_input = st.text_input("Type your question here:", key="chat_input")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        if user_input.lower() in ["hi", "hello", "hey"]:
            reply = "Hi! I’m your assistant. Ask me anything about the website you just searched."
        else:
            qa = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
            try:
                result = qa(question=user_input, context=st.session_state.summary)
                reply = result["answer"]
            except:
                reply = "Sorry, I couldn’t find an answer."

        st.session_state.messages.append({"role": "bot", "content": reply})
        st.markdown(f"**Bot:** {reply}")
