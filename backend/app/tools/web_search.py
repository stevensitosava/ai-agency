"""Web search tool — Tavily API.

Returns a list of {title, url, content} dicts for an LLM to consume.
Free tier: 1,000 searches/month.
"""

from __future__ import annotations

import os
from typing import Any

from tavily import TavilyClient


_client: TavilyClient | None = None


def _get_client() -> TavilyClient:
    global _client
    if _client is None:
        key = os.environ.get("TAVILY_API_KEY")
        if not key:
            raise RuntimeError("TAVILY_API_KEY not set in environment")
        _client = TavilyClient(api_key=key)
    return _client


def web_search(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Run a web search and return the top results.

    Returns a list of dicts with keys: title, url, content (snippet).
    """
    resp = _get_client().search(
        query=query,
        max_results=max_results,
        search_depth="basic",
        include_answer=False,
    )
    return [
        {"title": r["title"], "url": r["url"], "content": r["content"]}
        for r in resp.get("results", [])
    ]


# Function declaration for Gemini tool-use API
FUNCTION_DECLARATION = {
    "name": "web_search",
    "description": (
        "Search the web for information about a topic. "
        "Returns up to 5 results, each with a title, URL, and content snippet. "
        "Use this when you need facts, current data, or information not in your training data."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query. Be specific — 5-10 words usually works best.",
            },
            "max_results": {
                "type": "integer",
                "description": "How many results to return (1-10). Default 5.",
            },
        },
        "required": ["query"],
    },
}
