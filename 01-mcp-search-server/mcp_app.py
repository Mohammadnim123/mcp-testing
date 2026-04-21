from mcp.server.fastmcp import FastMCP
from search_tools import web_search as do_web_search, image_search as do_image_search

mcp_server = FastMCP("serp-search-mcp", host="0.0.0.0", port=3002)


@mcp_server.tool()
async def web_search(query: str) -> str:
    """Search the web using SerpAPI (Google). Use this to find current information on any topic."""
    return await do_web_search(query)


@mcp_server.tool()
async def image_search(query: str) -> str:
    """Search for images using SerpAPI (Google Images). Use this to find images on any topic."""
    return await do_image_search(query)
