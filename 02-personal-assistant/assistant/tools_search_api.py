import os

import httpx
from langchain_core.tools import tool


@tool
async def serp_api_search_tool(query: str) -> str:
    """Search the web using SerpAPI (Google). Use this to find current information on any topic."""
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY environment variable is not set")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "google",
                "q": query,
                "api_key": api_key,
                "num": 5,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    results = data.get("organic_results", [])[:5]
    if not results:
        return "No results found."

    formatted = []
    for r in results:
        title = r.get("title", "No title")
        link = r.get("link", "")
        snippet = r.get("snippet", "No description")
        formatted.append(f"**{title}**\n{link}\n{snippet}")
    return "\n\n".join(formatted)


@tool
async def serp_api_image_search_tool(query: str) -> str:
    """Search for images using SerpAPI (Google Images). Use this to find images on any topic."""
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY environment variable is not set")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "google_images",
                "q": query,
                "api_key": api_key,
                "num": 5,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    results = data.get("images_results", [])[:5]
    if not results:
        return "No image results found."

    formatted = []
    for r in results:
        title = r.get("title", "Image")
        original = r.get("original", "")
        source = r.get("source", "")
        line = f"![{title}]({original})"
        if source:
            line += f"\n_Source: {source}_"
        formatted.append(line)
    return "\n\n".join(formatted)
