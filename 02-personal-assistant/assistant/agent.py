import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

SYSTEM_MESSAGE = """You are a helpful personal assistant. Always use your tools when available.
For any questions about current events, facts, or information, use the search tools.
IMPORTANT: When tool output contains markdown image syntax like ![alt](url), preserve it exactly in your response."""


async def run_agent(message: str, session_id: str = "default", mode: str = "rag") -> dict:
    """Run the LangChain agent with the specified mode."""

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    thread_id = f"{session_id}-{mode}"
    client = None

    if mode == "rag":
        from .tools import search_knowledge_base
        tools = [search_knowledge_base]

    elif mode == "api":
        from .tools_search_api import serp_api_search_tool, serp_api_image_search_tool
        tools = [serp_api_search_tool, serp_api_image_search_tool]

    elif mode == "mcp":
        from langchain_mcp_adapters.client import MultiServerMCPClient
        client = MultiServerMCPClient({
            "search": {
                "url": "http://localhost:3002/mcp",
                "transport": "streamable_http",
            }
        })
        await client.__aenter__()
        tools = client.get_tools()

    elif mode == "mcp-stdio":
        from langchain_mcp_adapters.client import MultiServerMCPClient
        client = MultiServerMCPClient({
            "search": {
                "command": "python",
                "args": [
                    os.path.join(
                        os.path.dirname(__file__),
                        "..", "..",
                        "01-mcp-search-server", "stdio_server.py",
                    )
                ],
                "transport": "stdio",
                "env": {
                    "SERPAPI_API_KEY": os.environ.get("SERPAPI_API_KEY", ""),
                },
            }
        })
        await client.__aenter__()
        tools = client.get_tools()

    else:
        raise ValueError(f"Unknown mode: {mode}")

    agent = create_react_agent(
        llm,
        tools,
        checkpointer=checkpointer,
        prompt=SYSTEM_MESSAGE,
    )

    try:
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": thread_id}},
        )

        output = result["messages"][-1].content
        if not output or not output.strip():
            output = "I'm sorry, I couldn't generate a response. Please try again."

        return {"answer": output, "mode": mode}
    finally:
        if client is not None:
            try:
                await client.__aexit__(None, None, None)
            except Exception:
                pass
