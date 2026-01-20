from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import logging

@tool
def web_search(query: str) -> str:
    """Useful for searching the web for current information or recent events"""
    logging.info(f"Web search called with query: {query}")
    search = DuckDuckGoSearchRun()
    results = search.run(query)
    logging.info("Web search completed successfully")
    return results
