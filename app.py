import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from openai import OpenAI
from openai.error import RateLimitError

# Set up OpenAI client using Streamlit secrets
client = OpenAI(api_key=st.secrets["openai_api_key"])

st.set_page_config(page_title="AI Market Research Tool")
st.title("AI Market Research Tool")
st.write("Enter a business website URL below to get a market research summary.")

# Input for website URL
url = st.text_input("Website URL", placeholder="https://example.com")

# Function to scrape the content of a webpage
def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        # Extract visible text
        for script in soup(["script", "style"]):
            script.decompose()
        text = ' '.join(soup.stripped_strings)
        return text[:4000]  # Limit to 4000 characters
    except Exception as e:
        return f"Error scraping website: {e}"

# Function to generate summary using OpenAI with retry
def generate_summary(content):
    retries = 3
    for i in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful market research assistant."},
                    {"role": "user", "content": f"Summarize this business website content:\n\n{content}"}
                ]
            )
            return response.choices[0].message.content.strip()
        except RateLimitError:
            if i < retries - 1:
                time.sleep(2)  # Wait before retrying
            else:
                return "Rate limit exceeded. Please try again later."

# Run when user enters a URL
if url:
    with st.spinner("Scraping website..."):
        scraped_content = scrape_website(url)

    if "Error" not in scraped_content:
        with st.spinner("Generating summary..."):
            summary = generate_summary(scraped_content)
        st.subheader("Market Research Summary")
        st.write(summary)
    else:
        st.error(scraped_content)
