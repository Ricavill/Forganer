import json

import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from app.core.config import settings


def _http_client(token: str) -> httpx2.AsyncClient:
    return httpx2.AsyncClient(headers={"Authorization": f"Bearer {token}"})


async def list_openai_tools(token: str) -> list[dict]:
    """Fetch the bot agent's available tools from the MCP server, translated into
    the OpenAI function-calling tool format."""
    async with _http_client(token) as http_client:
        async with streamable_http_client(settings.mcp_server_url, http_client=http_client) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()

    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,
            },
        }
        for tool in result.tools
    ]


async def call_tool(token: str, name: str, arguments: dict) -> str:
    """Invoke one MCP tool on behalf of the user identified by `token` and return
    its result as a string suitable for feeding back to the model."""
    async with _http_client(token) as http_client:
        async with streamable_http_client(settings.mcp_server_url, http_client=http_client) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)

    texts = [c.text for c in result.content if hasattr(c, "text")]
    output = "\n".join(texts) if texts else json.dumps([c.model_dump() for c in result.content])

    if result.is_error:
        raise RuntimeError(output)
    return output
