import os
import logging
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "duckduckgo").lower()

@tool
def web_search(query: str) -> str:
    """Useful for searching the web for current information or recent events"""
    logging.info(f"Web search called with query: {query}")

    if SEARCH_PROVIDER == "tavily":
        results = _search_tavily(query)
    else:
        try:
            results = _search_duckduckgo(query)
        except Exception as e:
            logging.warning(f"DuckDuckGo search failed: {e}. Falling back to Tavily.")
            results = _search_tavily(query)

    logging.info("Web search completed successfully")
    return results


def _search_duckduckgo(query: str) -> str:
    search = DuckDuckGoSearchRun()
    return search.run(query)


def _search_tavily(query: str) -> str:
    from tavily import TavilyClient

    client = TavilyClient()
    response = client.search(query=query, max_results=5, search_depth="basic")
    results = response.get("results", [])
    return "\n\n".join(
        f"{r['title']}\n{r['url']}\n{r.get('content', '')}" for r in results
    )
