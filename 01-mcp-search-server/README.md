# MCP Search Server (Python)

A Model Context Protocol (MCP) search server exposing `web_search` and `image_search` tools backed by SerpAPI.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure your API key:

```bash
cp .env.example .env
# Edit .env and add your SerpAPI key
```

## Running

### HTTP transport (Streamable HTTP on port 3002)

```bash
python server.py
```

### Stdio transport

```bash
python stdio_server.py
```

## Tools

- **web_search(query)** - Search the web via Google and return the top 5 results.
- **image_search(query)** - Search Google Images and return the top 5 image results.
