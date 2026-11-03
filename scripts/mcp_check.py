import asyncio
import os
import sys
from pathlib import Path

import httpx2
from mcp import Client
from mcp.client.stdio import StdioServerParameters
from mcp.client.streamable_http import streamable_http_client

from app.core.config import get_settings

ARG = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/mcp"


def connect() -> Client:
    if ARG == "stdio":
        root = Path(__file__).resolve().parent.parent
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "app.mcp.stdio"],
            cwd=root,
            env=dict(os.environ),
        )
        return Client(params)
    secret = getattr(get_settings(), "MCP_API_KEY", None)
    key = secret.get_secret_value() if secret else ""
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    http = httpx2.AsyncClient(headers=headers)
    return Client(streamable_http_client(ARG, http_client=http))


async def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    async with connect() as client:
        print(f"Connected to {ARG}\n")
        print("TOOLS")
        for tool in (await client.list_tools()).tools:
            print(f"  {tool.name}: {(tool.description or '').split('.')[0]}")

        print("\nCALL search_products")
        args = {"category": "phone", "max_price": 40000}
        result = await client.call_tool("search_products", args)
        print(result.content[0].text)

        caps = client.server_capabilities
        if caps.resources:
            print("\nRESOURCE TEMPLATES")
            for t in (await client.list_resource_templates()).resource_templates:
                print(f"  {t.uri_template}")
        if caps.prompts:
            print("\nPROMPTS")
            for p in (await client.list_prompts()).prompts:
                print(f"  {p.name}: {p.description}")


if __name__ == "__main__":
    asyncio.run(main())
