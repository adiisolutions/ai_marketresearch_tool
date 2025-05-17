import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
from openai import OpenAI

# Setup OpenAI client using the new API
client = OpenAI(api_key=st.secrets.get("openai_api_key", "sk-..."))

st.set_page_config(page_title="Market Research Tool", layout="centered")
st.title("AI Market Research Agent")
st.write("Enter a website URL and get a sales-pitch-ready summary.")

# Input
url = st.text_input("Enter the Website URL:", placeholder="https://example.com")
generate = st.button("Generate Summary")


def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except Exception as e:
        return f"Error scraping website: {str(e)}"


def generate_summary(content):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes website content for a sales pitch."},
            {"role": "user", "content": f"Summarize this for a sales pitch:\n\n{content}"}
        ]
    )
    return response.choices[0].message.content


# Action
if generate and url:
    scraped_content = scrape_website(url)
    if "Error" in scraped_content:
        st.error(scraped_content)
    else:
        with st.spinner("Generating summary..."):
            summary = generate_summary(scraped_content)
            st.success("Summary generated!")
            st.write(summary)
