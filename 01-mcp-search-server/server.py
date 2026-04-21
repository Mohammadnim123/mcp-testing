from dotenv import load_dotenv

load_dotenv()

from mcp_app import mcp_server  # noqa: E402

if __name__ == "__main__":
    mcp_server.run(transport="streamable-http", host="0.0.0.0", port=3002)
