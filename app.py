import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

# Set Streamlit page configuration
st.set_page_config(page_title="AI Market Research Tool", layout="centered")

# App Title
st.title("AI Market Research Tool")
st.caption("Paste a website URL to extract and summarize public market-related content.")

# Disclaimer
st.markdown(
    """
    **Disclaimer:** This tool only summarizes content from websites that allow crawling via their `robots.txt`.
    It is your responsibility to ensure that you have the right to access and use the content from the provided URL.
    """
)

# URL input
url = st.text_input("Enter Website URL")

def is_scraping_allowed(website_url):
    try:
        parsed_url = urlparse(website_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = f"{base_url}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch("*", website_url)
    except:
        return False  # Assume disallowed if error occurs

def scrape_website(website_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(website_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)
        return text.strip()
    except:
        return ""

def generate_summary(text):
    if len(text.split()) < 50:
        return "The content is too short to generate a detailed summary."
    
    prompt = (
        "You are an expert market research AI. Expand the following content into a clear, insightful, and detailed market research summary. "
        "Write it in professional tone with subtitles:\n\n"
        f"{text}"
    )

    api_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer YOUR_OPENROUTER_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500
    }

    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Failed to generate summary. Status: {response.status_code}\n{response.text}"

if url:
    st.info("Checking website permissions...")
    if is_scraping_allowed(url):
        st.success("Scraping allowed. Extracting and summarizing content...")
        content = scrape_website(url)
        if content:
            summary = generate_summary(content)
            st.markdown("### Generated Market Research Summary")
            st.write(summary)
        else:
            st.warning("The website has very little readable content or failed to load.")
    else:
        st.error("Scraping is not allowed on this website per its robots.txt file.")
