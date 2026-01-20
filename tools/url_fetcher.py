from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
import logging

@tool
def fetch_webpage(url: str) -> str:
    """Fetches and extracts text content from a webpage URL"""
    logging.info(f"Fetching webpage: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text()[:5000]
        logging.info("Webpage fetched successfully")
        return text
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection error: {e}")
        return "Error: Invalid URL or could not connect"
    except requests.exceptions.Timeout as e:
        logging.error(f"Timeout error: {e}")
        return "Error: Request timed out"
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error: {e}")
        return f"Error: HTTP {e.response.status_code}"
    except Exception as e:
        logging.error(f"Error fetching webpage: {e}")
        return f"Error fetching website: {e}"
