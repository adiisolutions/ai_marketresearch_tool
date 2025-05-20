import streamlit as st
import urllib.robotparser
from urllib.parse import urlparse

def can_scrape(url, user_agent="*"):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    robots_url = f"{base_url}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        # If can't read robots.txt, allow scraping cautiously
        return True
    return rp.can_fetch(user_agent, url)

st.set_page_config(page_title="Market Research Summary Tool with ToS Check", layout="wide")
st.title("Market Research Summary Tool")

st.markdown("""
This tool respects website scraping policies via robots.txt.  
**Please confirm you have the right to scrape and use the data from the provided URL or text input.**  
""")

tos_confirmed = st.checkbox("I confirm I have read and will comply with the target website's Terms of Service and legal restrictions.")

input_type = st.radio("Input type:", ("Paste Text", "Enter URL to scrape"))

user_input = None
if input_type == "Paste Text":
    user_input = st.text_area("Paste market content here:", height=200)
elif input_type == "Enter URL to scrape":
    user_input = st.text_input("Enter website URL:")

if st.button("Generate Summary"):
    if not tos_confirmed:
        st.error("You must confirm compliance with website Terms of Service before proceeding.")
        st.stop()

    if not user_input or user_input.strip() == "":
        st.warning("Please provide text or URL input.")
        st.stop()

    if input_type == "Enter URL to scrape":
        if not can_scrape(user_input):
            st.error("Scraping disallowed by website's robots.txt. Please provide text manually or try another URL.")
            st.stop()
        else:
            st.info("Scraping allowed by robots.txt. Proceeding to scrape... (Simulated here)")
            # Simulate scraping - replace with actual scraping code
            scraped_text = "Simulated scraped content from the URL."
    else:
        scraped_text = user_input

    # Simulate AI summary generation (replace this with your AI API call)
    summary = f"--- AI Generated Summary (Simulated) ---\n\nInput length: {len(scraped_text)} characters.\n\nSummary would be generated here."

    st.success("Summary generated successfully!")
    st.text_area("AI-Generated Summary:", value=summary, height=300)

st.markdown("---")
st.markdown("""
### Disclaimer  
This tool checks website `robots.txt` to respect crawling policies but **cannot guarantee full legal compliance** with website Terms of Service or copyright laws.  
Users are solely responsible for ensuring that their scraping and use of data complies with all applicable laws and website terms.  
By using this tool, you agree to comply with all relevant legal restrictions.
""")
