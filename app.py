import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import os

# Set your OpenAI API key here or in Streamlit Secrets
openai.api_key = st.secrets.get("openai_api_key", "sk-...")  # Replace with your key or use secrets

st.set_page_config(page_title="Market Research Tool", layout="centered")

st.title("AI Market Research Agent")
st.write("Enter a website URL and get a sales-pitch-ready summary.")

# Input
url = st.text_input("Enter the Website URL:", placeholder="https://example.com")
generate = st.button("Generate Summary")

def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Extract text from paragraphs
        paragraphs = soup.find_all('p')
        text = " ".join([para.get_text() for para in paragraphs])

        return text[:5000]  # Limit to 5000 chars
    except Exception as e:
        return f"Error scraping website: {e}"

def generate_summary(content):
    prompt = f"""
Can you please take this website content and summarize it into a 300-word natural language summary?

Break it into key areas like:
- Overview
- Products & Services
- Team
- Recent News or Blogs

Do not return JSON. Make it readable for a sales rep.

Website Content:
\"\"\"
{content}
\"\"\"
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use gpt-4 if you have access
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error with OpenAI API: {e}"

if generate and url:
    with st.spinner("Scraping and generating summary..."):
        scraped_text = scrape_website(url)
        if "Error" in scraped_text:
            st.error(scraped_text)
        else:
            summary = generate_summary(scraped_text)
            st.success("Summary generated!")
            st.markdown(summary)
