import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Set up the OpenAI client using the key from secrets
client = OpenAI(api_key=st.secrets["openai_api_key"])

# Function to scrape website text
def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract visible text
        texts = soup.stripped_strings
        return " ".join(texts)[:4000]  # Limit to 4000 characters for token limit
    except Exception as e:
        return f"Error scraping website: {e}"

# Function to generate a summary using OpenAI
def generate_summary(content):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful market research assistant."},
                {"role": "user", "content": f"Summarize this business website content in a human-readable format for sales research:\n\n{content}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {e}"

# Streamlit interface
st.title("Market Research AI Tool")
url = st.text_input("Enter website URL")

if st.button("Generate Summary") and url:
    with st.spinner("Scraping and analyzing..."):
        scraped_content = scrape_website(url)
        if scraped_content.startswith("Error"):
            st.error(scraped_content)
        else:
            summary = generate_summary(scraped_content)
            st.subheader("Summary:")
            st.write(summary)
