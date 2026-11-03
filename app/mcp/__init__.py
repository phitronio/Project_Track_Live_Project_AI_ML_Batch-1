import json
from typing import Any

from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import (
    StreamableHTTPASGIApp,
    StreamableHTTPSessionManager,
)

from app.db.session import SessionLocal
from app.integrations.embeddings.dependencies import get_embedding_client
from app.modules.catalog.repositories import ProductRepository
from app.modules.catalog.services import ProductService
from app.modules.chat.tools import TOOLS, execute_tool
from app.modules.knowledge.repositories import KnowledgeRepository
from app.modules.knowledge.services import KnowledgeService


async def list_tools(ctx, params) -> types.ListToolsResult:
    tools = [
        types.Tool(
            name=spec.name,
            description=spec.description,
            input_schema=spec.parameters,
        )
        for spec in TOOLS
    ]
    return types.ListToolsResult(tools=tools)


async def call_tool(ctx, params: types.CallToolRequestParams) -> types.CallToolResult:
    async with SessionLocal() as session:
        products = ProductService(ProductRepository(session))
        knowledge = KnowledgeService(
            KnowledgeRepository(session), get_embedding_client()
        )
        result: dict[str, Any] = await execute_tool(
            products, knowledge, params.name, params.arguments or {}
        )
    return types.CallToolResult(
        content=[types.TextContent(text=json.dumps(result, ensure_ascii=False))],
        is_error="error" in result,
    )


server = Server("kinbo", on_list_tools=list_tools, on_call_tool=call_tool)

session_manager = StreamableHTTPSessionManager(app=server)
mcp_asgi_app = StreamableHTTPASGIApp(session_manager)
