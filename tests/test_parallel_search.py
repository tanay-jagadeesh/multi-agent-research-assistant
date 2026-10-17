"""Offline MCP protocol and scripted agent tests; no model API calls."""
import asyncio
import importlib
import json
import os
import unittest
from unittest.mock import patch

import httpx
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field

from tools import web_search
from tools import parallel_search

QUERY = "LangGraph research sources"
EVIDENCE = "LangGraph documentation\nhttps://docs.langchain.com/oss/python/langgraph/overview\nStateful agent orchestration."
REAL_CLIENT = httpx.AsyncClient


def leaf_errors(error):
    if isinstance(error, BaseExceptionGroup):
        return [leaf for child in error.exceptions for leaf in leaf_errors(child)]
    return [error]


class MCPServer:
    """Drive the real MCP SDK with recorded HTTP requests and JSON-RPC replies."""

    def __init__(self, mode="ok"):
        self.mode = mode
        self.requests = []
        self.call_started = asyncio.Event()
        self.clients = []

    def client(self, **kwargs):
        client = REAL_CLIENT(transport=httpx.MockTransport(self.handle), **kwargs)
        self.clients.append(client)
        return client

    async def handle(self, request):
        body = json.loads(request.content)
        self.requests.append((request, body))
        method = body["method"]
        if self.mode == "forbidden":
            return httpx.Response(403, text="Forbidden")
        if "id" not in body:
            return httpx.Response(202)
        if method == "initialize":
            result = {
                "protocolVersion": body["params"]["protocolVersion"],
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "fixture", "version": "1"},
            }
        elif method == "tools/list":
            result = {"tools": [] if self.mode == "missing" else [{
                "name": "web_search", "description": "Search the web",
                "inputSchema": {"type": "object", "properties": {
                    "objective": {"type": "string"},
                    "search_queries": {"type": "array", "items": {"type": "string"}},
                }, "required": ["objective", "search_queries"]},
            }]}
        elif method == "tools/call":
            self.call_started.set()
            if self.mode == "wait":
                await asyncio.Event().wait()
            if self.mode == "malformed":
                return httpx.Response(200, text="not JSON", headers={"Content-Type": "application/json"})
            result = {"content": [] if self.mode == "empty" else [{
                "type": "text", "text": "Service unavailable" if self.mode == "error" else EVIDENCE,
            }], "isError": self.mode == "error"}
        else:
            raise AssertionError(f"Unexpected MCP method: {method}")
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": body["id"], "result": result})

    def patch(self):
        return patch("tools.parallel_search.httpx.AsyncClient", side_effect=self.client)


class ScriptedResearchModel(BaseChatModel):
    """Request web_search, then consume its ToolMessage in the actual agent loop."""
    observed: list[str] = Field(default_factory=list)

    @property
    def _llm_type(self):
        return "scripted-search-test"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        if isinstance(messages[-1], ToolMessage):
            self.observed.append(messages[-1].content)
            message = AIMessage(content="Cited finding: " + messages[-1].content)
        else:
            message = AIMessage(content="", tool_calls=[{
                "name": "web_search", "args": {"query": QUERY}, "id": "search-1",
            }])
        return ChatResult(generations=[ChatGeneration(message=message)])


class SearchDispatchTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_unconfigured_and_explicit_duckduckgo(self):
        with patch("langchain_community.tools.DuckDuckGoSearchRun") as duck, \
                patch("tools.parallel_search.search") as parallel:
            duck.return_value.run.return_value = "Existing DuckDuckGo output"
            self.assertEqual(web_search.invoke({"query": QUERY}), "Existing DuckDuckGo output")
            os.environ["SEARCH_PROVIDER"] = "duckduckgo"
            self.assertEqual(web_search.invoke({"query": QUERY}), "Existing DuckDuckGo output")
            self.assertEqual(duck.return_value.run.call_count, 2)
            parallel.assert_not_called()

    def test_disabled_invalid_and_explicit_failure_do_not_fallback(self):
        with patch("tools.web_search._search_duckduckgo") as duck, \
                patch("tools.parallel_search.search", side_effect=RuntimeError("provider failed")) as parallel:
            os.environ["SEARCH_PROVIDER"] = "none"
            self.assertIn("disabled", web_search.invoke({"query": QUERY}))
            os.environ["SEARCH_PROVIDER"] = "tavily"
            with self.assertRaisesRegex(ValueError, "SEARCH_PROVIDER"):
                web_search.invoke({"query": QUERY})
            parallel.assert_not_called()
            os.environ["SEARCH_PROVIDER"] = "parallel"
            with self.assertRaisesRegex(RuntimeError, "provider failed"):
                web_search.invoke({"query": QUERY})
            duck.assert_not_called()

    def test_both_agent_factories_consume_mcp_results(self):
        os.environ["SEARCH_PROVIDER"] = "parallel"
        for module, factory in [
            ("agents.research_agent", "create_research_agent"),
            ("agents.fact_checker_agent", "create_fact_checker_agent"),
        ]:
            with self.subTest(factory=factory):
                model = ScriptedResearchModel()
                server = MCPServer()
                agent_module = importlib.import_module(module)
                with patch.object(agent_module, "get_llm", return_value=model), server.patch():
                    agent, _ = getattr(agent_module, factory)()
                    result = agent.invoke(
                        {"messages": [{"role": "user", "content": QUERY}]},
                        {"configurable": {"thread_id": factory}},
                    )
                self.assertEqual(model.observed, [EVIDENCE])
                self.assertIn("https://docs.langchain.com/", result["messages"][-1].content)
                for request, body in server.requests:
                    self.assertEqual(str(request.url), parallel_search.MCP_URL)
                    self.assertEqual(request.headers["User-Agent"], parallel_search.USER_AGENT)
                    self.assertNotIn("Authorization", request.headers)
                call = next(b for _, b in server.requests if b["method"] == "tools/call")
                self.assertEqual(call["params"]["name"], "web_search")
                self.assertEqual(call["params"]["arguments"], {
                    "objective": QUERY, "search_queries": [QUERY],
                })
                self.assertTrue(all(client.is_closed for client in server.clients))

    def test_errors_and_permission_denial_propagate(self):
        os.environ["SEARCH_PROVIDER"] = "parallel"
        for mode in ("forbidden", "missing", "error", "empty", "malformed"):
            with self.subTest(mode=mode):
                server = MCPServer(mode)
                with server.patch(), patch("tools.web_search._search_duckduckgo") as duck, \
                        patch.object(parallel_search, "TIMEOUT_SECONDS", 0.5):
                    with self.assertRaises(Exception) as caught:
                        web_search.invoke({"query": QUERY})
                    duck.assert_not_called()
                errors = leaf_errors(caught.exception)
                if mode == "forbidden":
                    self.assertTrue(any(isinstance(e, httpx.HTTPStatusError) and
                                        e.response.status_code == 403 for e in errors))
                elif mode == "malformed":
                    # The SDK logs invalid JSON, then the overall deadline expires.
                    self.assertTrue(any(isinstance(e, TimeoutError) for e in errors))
                else:
                    expected = {"missing": "does not expose web_search",
                                "error": "Service unavailable", "empty": "no text results"}[mode]
                    self.assertTrue(any(isinstance(e, RuntimeError) and expected in str(e) for e in errors))
                self.assertTrue(all(client.is_closed for client in server.clients))
                if mode == "missing":
                    self.assertFalse(any(b["method"] == "tools/call" for _, b in server.requests))


class AsyncSearchTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.env = patch.dict(os.environ, {"SEARCH_PROVIDER": "parallel"}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    async def test_async_dispatch(self):
        server = MCPServer()
        with server.patch():
            self.assertEqual(await web_search.ainvoke({"query": QUERY}), EVIDENCE)

    async def test_timeout_covers_transport_and_closes_client(self):
        server = MCPServer("wait")
        with server.patch(), patch.object(parallel_search, "TIMEOUT_SECONDS", 0.1):
            with self.assertRaises(TimeoutError):
                await web_search.ainvoke({"query": QUERY})
        self.assertTrue(server.call_started.is_set())
        self.assertTrue(all(client.is_closed for client in server.clients))

    async def test_cancellation_closes_client(self):
        server = MCPServer("wait")
        with server.patch():
            task = asyncio.create_task(web_search.ainvoke({"query": QUERY}))
            await asyncio.wait_for(server.call_started.wait(), timeout=2)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        self.assertTrue(all(client.is_closed for client in server.clients))

    async def test_disabled_async_never_connects(self):
        os.environ["SEARCH_PROVIDER"] = "none"
        with patch("tools.parallel_search.httpx.AsyncClient") as client:
            self.assertIn("disabled", await web_search.ainvoke({"query": QUERY}))
            client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
