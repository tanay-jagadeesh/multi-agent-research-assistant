"""Anonymous Parallel Search MCP adapter for the shared research search tool."""
import asyncio
from datetime import timedelta

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import Implementation, TextContent

MCP_URL = "https://search.parallel.ai/mcp"
USER_AGENT = (
    "multi-agent-research-assistant "
    "(+https://github.com/tanay-jagadeesh/multi-agent-research-assistant)"
)
TIMEOUT_SECONDS = 30


async def search(query: str) -> str:
    """Return server excerpts with their source URLs, or propagate failures.

    No keys, account settings or fallback providers are consulted. A single
    deadline covers connection, discovery, search and transport cleanup.
    """
    async with asyncio.timeout(TIMEOUT_SECONDS):
        async with httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT_SECONDS,
        ) as client:
            async with streamable_http_client(MCP_URL, http_client=client) as streams:
                async with ClientSession(
                    streams[0], streams[1],
                    read_timeout_seconds=timedelta(seconds=TIMEOUT_SECONDS),
                    client_info=Implementation(
                        name="multi-agent-research-assistant", version="unversioned"
                    ),
                ) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    if not any(tool.name == "web_search" for tool in tools.tools):
                        raise RuntimeError("Parallel MCP does not expose web_search")
                    result = await session.call_tool(
                        "web_search",
                        {"objective": query, "search_queries": [query]},
                    )
                    text = "\n\n".join(
                        block.text for block in result.content
                        if isinstance(block, TextContent)
                    )
                    if result.isError:
                        raise RuntimeError(f"Parallel search failed: {text}")
                    if not text.strip():
                        raise RuntimeError("Parallel search returned no text results")
                    return text
