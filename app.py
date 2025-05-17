import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import httpx

# Get OpenRouter API key from secrets
API_KEY = st.secrets["openrouter_api_key"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"

st.set_page_config(page_title="AI Market Research Tool (OpenRouter)")
st.title("AI Market Research Tool using OpenRouter")
st.write("Enter a business website URL to get a detailed market research analysis.")

url = st.text_input("Website URL", placeholder="https://example.com")

def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        text = ' '.join(soup.stripped_strings)
        return text[:4000]  # Limit to first 4000 chars to avoid token limits
    except Exception as e:
        return f"Error scraping website: {e}"

def generate_summary(content):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    json_data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a market research expert."},
            {"role": "user", "content": f"""
You are a market research expert. Analyze the following business website content carefully and provide:

1. A detailed explanation of what the business does.
2. Its target audience.
3. Unique selling points.
4. Potential market challenges.
5. Suggestions for improving marketing or sales strategies.

Content to analyze:
{content}
"""}
        ]
    }

    retries = 3
    for i in range(retries):
        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(API_URL, headers=headers, json=json_data)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except httpx.HTTPStatusError as e:
            if response.status_code == 429 and i < retries - 1:
                time.sleep(2)
            else:
                return "Rate limit exceeded or HTTP error. Please try again later."
        except Exception as e:
            return f"Error: {e}"

if url:
    with st.spinner("Scraping website..."):
        scraped_content = scrape_website(url)

    if not scraped_content.startswith("Error"):
        with st.spinner("Generating detailed market research..."):
            summary = generate_summary(scraped_content)
        st.subheader("Detailed Market Research Analysis")
        st.write(summary)
    else:
        st.error(scraped_content)
