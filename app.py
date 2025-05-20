import streamlit as st
import requests

# --- Configuration ---
st.set_page_config(page_title="Market Research & Chatbot Tool", layout="wide")

# Initialize session state for chatbot visibility and chat history
if "chat_visible" not in st.session_state:
    st.session_state.chat_visible = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def toggle_chat():
    st.session_state.chat_visible = not st.session_state.chat_visible

# Header with toggle button (chat icon)
st.markdown(
    """
    <style>
    .chat-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #007bff;
        color: white;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 30px;
        text-align: center;
        cursor: pointer;
        z-index: 9999;
        line-height: 60px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="chat-button" onclick="window.parent.postMessage({{type: \'toggle_chat\'}}, \'*\')">&#128172;</div>',
    unsafe_allow_html=True,
)

# Streamlit button alternative for toggle (for local testing)
st.button("Toggle Chatbot", on_click=toggle_chat)

# Chatbot UI
if st.session_state.chat_visible:
    st.markdown("### Chatbot")
    user_input = st.text_input("Ask me anything about your market data:")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        headers = {
            "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": st.session_state.chat_history,
            "max_tokens": 500,
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            bot_reply = result["choices"][0]["message"]["content"]
            st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        else:
            bot_reply = "Sorry, I couldn't process your request."

        st.write(f"**Bot:** {bot_reply}")

    # Show chat history
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f"**You:** {chat['content']}")
        else:
            st.markdown(f"**Bot:** {chat['content']}")
