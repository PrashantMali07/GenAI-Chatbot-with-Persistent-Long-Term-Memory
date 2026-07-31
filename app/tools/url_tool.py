import requests
from bs4 import BeautifulSoup
from langchain_community.tools import tool


@tool
def get_url_content(url: str) -> str:
    """
    CRITICAL: Use this tool ONLY when the user provides an exact website URL link 
    (starting with http:// or https://) and asks to extract information directly from it.
    
    DO NOT use Wikipedia or DuckDuckGo if a specific direct URL is provided. 
    Input must be a single, valid, raw URL string.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"Error: Webpage returned status code {response.status_code}"
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # --- FIXING THE HTML SNIPPET ISSUE ---
        # If it's Google Scholar, extract just the authors so we don't dump raw HTML to the LLM
        if "scholar.google" in url:
            for field in soup.find_all("div", class_="gsc_oci_field"):
                if "Authors" in field.get_text():
                    value_div = field.find_next_sibling("div", class_="gsc_oci_value")
                    if value_div:
                        return f"Data successfully extracted from URL. Authors: {value_div.get_text(strip=True)}"
            return "Connected to Google Scholar, but could not find the Authors block."
            
        # For any other general website, strip out the HTML tags and return pure text
        # This stops the LLM from getting drowned in `<!DOCTYPE html>` codes
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose() 
        return f"Webpage content text: {soup.get_text()[:2000]}" # Limit characters to save tokens
        
    except Exception as e:
        return f"An error occurred while fetching the URL: {str(e)}"