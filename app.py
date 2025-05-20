import streamlit as st import requests from bs4 import BeautifulSoup from urllib.parse import urlparse from urllib.robotparser import RobotFileParser

def is_scraping_allowed(url): parsed_url = urlparse(url) base_url = f"{parsed_url.scheme}://{parsed_url.netloc}" robots_url = f"{base_url}/robots.txt"

rp = RobotFileParser()
try:
    rp.set_url(robots_url)
    rp.read()
    return rp.can_fetch("*", url)
except:
    return False  # Assume disallowed if robots.txt is missing or unreadable

def extract_text_from_url(url): try: response = requests.get(url, timeout=10) soup = BeautifulSoup(response.text, "html.parser") paragraphs = soup.find_all("p") return " ".join([p.get_text() for p in paragraphs]) except: return ""

def generate_summary(content): if len(content) < 100: return "Content too short to summarize effectively."

prompt = f"""

You are a market research AI assistant. Read the following website content and generate a professional, detailed market analysis summary based on it. Focus on the business, offerings, customer appeal, industry trends, and strategic positioning. Make the summary easy to understand even for non-experts:

""" prompt += content

headers = {
    "Authorization": f"Bearer YOUR_OPENROUTER_API_KEY",
    "HTTP-Referer": "https://yourapp.com",
    "X-Title": "Market Research AI Tool"
}

data = {
    "model": "openrouter/mistralai/mistral-7b-instruct",
    "messages": [
        {"role": "user", "content": prompt},
    ],
    "max_tokens": 1500
}

response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data

