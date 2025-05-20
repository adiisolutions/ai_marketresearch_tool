import streamlit as st
import requests
from bs4 import BeautifulSoup
from streamlit_chat import message
from transformers import pipeline

# ---- Page Setup ----
st.set_page_config(page_title="Market Research Tool", layout="wide")
st.title("AI Market Research & Chatbot Tool")

# ---- Session State Init ----
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = False

# ---- Functions ----
@st.cache_data(show_spinner=True)
def scrape_and_summarize(url, word_limit):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join(p.get_text() for p in paragraphs)
        content = content[:6000]  # Truncate if too long

        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
        summary = summarizer(content, max_length=word_limit, min_length=100, do_sample=False)[0]['summary_text']
        return summary
    except Exception as e:
        return f"Error: {e}"

# ---- Sidebar ----
with st.sidebar:
    st.header("Market Research Tool")
    url = st.text_input("Enter Company URL")
    length = st.selectbox("Summary Length", options=["Short (~300 words)", "Detailed (1500+ words)"])
    word_limit = 300 if "300" in length else 1024  # 1024 is near the model’s max
    if st.button("Generate Summary"):
        if url:
            with st.spinner("Generating summary..."):
                summary = scrape_and_summarize(url, word_limit)
                st.session_state.summary = summary
                st.success("Summary generated!")

# ---- Show Summary ----
if st.session_state.summary:
    st.subheader("Website Summary")
    st.write(st.session_state.summary)

# ---- Toggle Chatbot ----
if st.button("Toggle Chatbot"):
    st.session_state.chatbot = not st.session_state.chatbot

# ---- Chatbot Section ----
if st.session_state.chatbot:
    st.markdown("---")
    st.subheader("Ask About the Website")

    for msg in st.session_state.messages:
        message(msg["content"], is_user=msg["role"] == "user")

    user_input = st.text_input("You:", key="chat_input")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        if not st.session_state.summary:
            response = "Please generate a summary first using the Market Research Tool."
        elif user_input.lower() in ["hi", "hello", "hey"]:
            response = "Hi! I'm your website assistant. Ask me anything about the company you searched."
        else:
            context = st.session_state.summary
            qa_model = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
            try:
                answer = qa_model(question=user_input, context=context)
                response = answer['answer']
            except:
                response = "Sorry, I couldn't find an answer to that."

        st.session_state.messages.append({"role": "bot", "content": response})
        message(response, is_user=False)
