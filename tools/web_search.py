from langchain_core.tools import StructuredTool
import asyncio
import logging
import os


def _provider() -> str:
    """Resolve each call so explicit environment settings are respected."""
    provider = os.getenv("SEARCH_PROVIDER", "duckduckgo").strip().lower()
    if provider not in {"duckduckgo", "parallel", "none"}:
        raise ValueError("SEARCH_PROVIDER must be duckduckgo, parallel, or none")
    return provider


def _search_duckduckgo(query: str) -> str:
    from langchain_community.tools import DuckDuckGoSearchRun

    return DuckDuckGoSearchRun().run(query)


def _web_search(query: str) -> str:
    """Useful for searching the web for current information or recent events."""
    provider = _provider()
    if provider == "none":
        return "Web search is disabled (SEARCH_PROVIDER=none)."
    logging.info("Web search called with provider: %s", provider)
    if provider == "parallel":
        from .parallel_search import search

        return asyncio.run(search(query))
    return _search_duckduckgo(query)


async def _aweb_search(query: str) -> str:
    """Async dispatch preserves cancellation of the Parallel HTTP request."""
    provider = _provider()
    if provider == "none":
        return "Web search is disabled (SEARCH_PROVIDER=none)."
    if provider == "parallel":
        from .parallel_search import search

        return await search(query)
    return await asyncio.to_thread(_search_duckduckgo, query)


web_search = StructuredTool.from_function(
    _web_search, coroutine=_aweb_search, name="web_search"
)
