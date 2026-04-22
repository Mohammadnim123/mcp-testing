import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient

checkpointer = MemorySaver()

SYSTEM_MESSAGE = """You are a helpful personal assistant. Always use your tools when available.
For any questions about current events, facts, or information, use the search tools.
IMPORTANT: When tool output contains markdown image syntax like ![alt](url), preserve it exactly in your response."""

MCP_URL = "http://localhost:3002/mcp"


async def run_agent(message: str, session_id: str = "default", mode: str = "mcp") -> dict:
    """Run the LangChain agent in either MCP or RAG mode."""

    llm = ChatOpenAI(
        model=os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        temperature=0,
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    )
    thread_id = f"{session_id}-{mode}"

    if mode == "rag":
        from .tools import search_knowledge_base
        tools = [search_knowledge_base]

    elif mode == "mcp":
        client = MultiServerMCPClient({
            "search": {
                "url": MCP_URL,
                "transport": "streamable_http",
            }
        })
        tools = await client.get_tools()

    else:
        raise ValueError(f"Unknown mode: {mode}")

    agent = create_react_agent(
        llm,
        tools,
        checkpointer=checkpointer,
        prompt=SYSTEM_MESSAGE,
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": message}]},
        config={"configurable": {"thread_id": thread_id}},
    )

    output = result["messages"][-1].content
    if not output or not output.strip():
        output = "I'm sorry, I couldn't generate a response. Please try again."

    return {"answer": output, "mode": mode}
