import streamlit as st
import requests
import os

# --- Page config ---
st.set_page_config(page_title="Market Research Tool + Chatbot", layout="wide")

# --- API Key ---
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))
if not OPENROUTER_API_KEY:
    st.error("OpenRouter API key is missing.")
    st.stop()

# --- Chatbot toggle state ---
if 'chatbot_open' not in st.session_state:
    st.session_state.chatbot_open = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- Main Title ---
st.title("AI Market Research Summary Tool with Chatbot")

# --- Chatbot Toggle Button with emoji logo ---
toggle_button = st.button("💬 Chatbot")

if toggle_button:
    st.session_state.chatbot_open = not st.session_state.chatbot_open

# --- Show chatbot UI if toggled ON ---
if st.session_state.chatbot_open:
    st.markdown("### Chatbot — Ask questions based on the data")

    # Input box for user question
    user_question = st.text_input("Your question:", key="user_question_input")

    if user_question:
        # Show user message in chat history
        st.session_state.chat_history.append({"role": "user", "content": user_question})

        # Prepare messages for OpenRouter
        messages = [
            {"role": "system", "content": "You are a helpful market research assistant."},
        ] + st.session_state.chat_history

        # Call OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": messages,
            "max_tokens": 1500,
            "temperature": 0.7,
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            bot_reply = result["choices"][0]["message"]["content"]
            # Append bot reply to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
            # Clear input box
            st.session_state.user_question_input = ""

        else:
            bot_reply = f"Error: {response.status_code}"
            st.error(bot_reply)

    # Display chat history
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f"**You:** {chat['content']}")
        else:
            st.markdown(f"**Bot:** {chat['content']}")

# --- Your existing Market Research input, summary generation, etc. can be below or above ---


# For example (simplified, add your full code here)
st.markdown("---")
st.markdown("### Market Research Summary Section (Your existing code here)")
