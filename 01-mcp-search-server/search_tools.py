import os
import httpx

SERPAPI_BASE_URL = "https://serpapi.com/search.json"


async def web_search(query: str) -> str:
    """Call SerpAPI with engine=google and return the top 5 results."""
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "SERPAPI_API_KEY environment variable is not set. "
            "Please set it in your .env file or environment."
        )

    params = {
        "engine": "google",
        "q": query,
        "num": 5,
        "api_key": api_key,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(SERPAPI_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

    organic_results = data.get("organic_results", [])
    if not organic_results:
        return "No results found."

    formatted = []
    for result in organic_results[:5]:
        title = result.get("title", "No title")
        link = result.get("link", "")
        snippet = result.get("snippet", "No description available")
        formatted.append(f"**{title}**\n{link}\n{snippet}")

    return "\n\n".join(formatted)


async def image_search(query: str) -> str:
    """Call SerpAPI with engine=google_images and return the top 5 image results."""
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "SERPAPI_API_KEY environment variable is not set. "
            "Please set it in your .env file or environment."
        )

    params = {
        "engine": "google_images",
        "q": query,
        "num": 5,
        "api_key": api_key,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(SERPAPI_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

    images_results = data.get("images_results", [])
    if not images_results:
        return "No image results found."

    formatted = []
    for result in images_results[:5]:
        title = result.get("title", "Image")
        original = result.get("original", "")
        source = result.get("source", "Unknown source")
        formatted.append(f"![{title}]({original})\n_Source: {source}_")

    return "\n\n".join(formatted)
