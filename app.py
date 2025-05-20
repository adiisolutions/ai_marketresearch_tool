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
            scraped_text = "Simulated scraped content from the URL."
    else:
        scraped_text = user_input

    summary = f"--- AI Generated Summary (Simulated) ---\n\nInput length: {len(scraped_text)} characters.\n\nSummary would be generated here."

    st.success("Summary generated successfully!")
    st.text_area("AI-Generated Summary:", value=summary, height=300)

# Disclaimer placed outside of conditionals to always show
st.markdown("---")
st.markdown("""
### Disclaimer  
This tool performs a basic check of the website's `robots.txt` file to respect crawling policies.  
**However, it does NOT guarantee full compliance with the website’s Terms of Service or any copyright laws.**  

You, the user, are solely responsible for:  
- Ensuring your scraping and data usage complies with all applicable laws, regulations, and website terms.  
- Obtaining all necessary permissions before scraping or using data from any website.  
- Any legal consequences arising from misuse or unauthorized scraping.

By using this tool, you acknowledge and agree to comply with all relevant legal restrictions and accept full responsibility for your actions.
""")
