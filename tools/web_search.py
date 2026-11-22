"""Web search and scraping tool using Tavily API for market research."""

import os
from typing import Any
import config.settings  # noqa: F401 - Initialize environment before crewai imports
from crewai.tools import tool
from config.settings import TAVILY_API_KEY


def format_search_results(query: str, results: list[dict[str, Any]]) -> str:
    """Format raw Tavily results into clean, structured Markdown."""
    if not results:
        return f"No search results found for query: '{query}'"

    formatted_output = [f"### Web Search Results for: '{query}'\n"]
    for idx, item in enumerate(results, start=1):
        title = item.get("title", "Untitled Result").strip()
        url = item.get("url", "No URL provided").strip()
        content = item.get("content", "").strip()
        formatted_output.append(
            f"{idx}. **{title}**\n"
            f"   - **URL**: {url}\n"
            f"   - **Content**: {content}\n"
        )
    return "\n".join(formatted_output)


@tool("web_search_and_scrape")
def web_search_and_scrape(query: str) -> str:
    """Search the web using Tavily API and return structured results with titles, URLs, and summaries."""
    if not query or not query.strip():
        return "Error: Search query cannot be empty."

    api_key = TAVILY_API_KEY or os.getenv("TAVILY_API_KEY", "")
    if not api_key or not api_key.strip():
        return "Error: TAVILY_API_KEY is not configured in .env or environment."

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=api_key.strip())
        response = client.search(
            query=query.strip(),
            search_depth="basic",
            max_results=5,
            timeout=30,
        )
        results = response.get("results", [])
        return format_search_results(query.strip(), results)
    except Exception as exc:
        return f"Tavily search error: {str(exc)}"
