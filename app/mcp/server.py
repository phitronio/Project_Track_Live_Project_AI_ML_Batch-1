import json
from typing import Any

from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import (
    StreamableHTTPASGIApp,
    StreamableHTTPSessionManager,
)
from mcp.shared.exceptions import MCPError

from app.core.exceptions.errors import NotFoundError
from app.db.session import SessionLocal
from app.integrations.embeddings.dependencies import get_embedding_client
from app.modules.catalog.repositories import ProductRepository
from app.modules.catalog.schemas import ProductFilters
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


PRODUCT_URI = "kinbo://products/"


async def list_resources(ctx, params) -> types.ListResourcesResult:
    async with SessionLocal() as session:
        products = ProductService(ProductRepository(session))
        page = await products.get_all_products(ProductFilters(page_size=50))
    return types.ListResourcesResult(
        resources=[
            types.Resource(
                uri=f"{PRODUCT_URI}{p.slug}",
                name=p.name,
                mime_type="application/json",
            )
            for p in page.items
        ]
    )


async def list_resource_templates(
    ctx, params
) -> types.ListResourceTemplatesResult:
    template = types.ResourceTemplate(
        uri_template=f"{PRODUCT_URI}{{slug}}",
        name="product",
        description="One Kinbo product (specs, price, stock) as JSON.",
        mime_type="application/json",
    )
    return types.ListResourceTemplatesResult(resource_templates=[template])


async def read_resource(
    ctx, params: types.ReadResourceRequestParams
) -> types.ReadResourceResult:
    if not params.uri.startswith(PRODUCT_URI):
        raise MCPError(-32002, f"Unknown resource: {params.uri}")
    slug = params.uri.removeprefix(PRODUCT_URI)
    async with SessionLocal() as session:
        products = ProductService(ProductRepository(session))
        try:
            product = await products.get_product(slug)
        except NotFoundError as exc:
            raise MCPError(-32002, str(exc)) from exc
    text = json.dumps(product.model_dump(mode="json", exclude={"id"}))
    return types.ReadResourceResult(
        contents=[
            types.TextResourceContents(
                uri=params.uri, mime_type="application/json", text=text
            )
        ]
    )


COMPARE_PROMPT = types.Prompt(
    name="compare_products",
    description="Compare two Kinbo products for a customer.",
    arguments=[
        types.PromptArgument(name="slug_a", required=True),
        types.PromptArgument(name="slug_b", required=True),
    ],
)


async def list_prompts(ctx, params) -> types.ListPromptsResult:
    return types.ListPromptsResult(prompts=[COMPARE_PROMPT])


async def get_prompt(
    ctx, params: types.GetPromptRequestParams
) -> types.GetPromptResult:
    if params.name != COMPARE_PROMPT.name:
        raise MCPError(-32602, f"Unknown prompt: {params.name}")
    args = params.arguments or {}
    if "slug_a" not in args or "slug_b" not in args:
        raise MCPError(-32602, "Both slug_a and slug_b are required")
    text = (
        f"Compare the products '{args['slug_a']}' and '{args['slug_b']}' for a customer. "
        "Call get_product_details for each one, then show a short comparison "
        "(price in BDT, specs, warranty, stock) and say which one you recommend."
    )
    return types.GetPromptResult(
        messages=[
            types.PromptMessage(role="user", content=types.TextContent(text=text))
        ]
    )


server = Server(
    "kinbo",
    on_list_tools=list_tools,
    on_call_tool=call_tool,
    on_list_resources=list_resources,
    on_list_resource_templates=list_resource_templates,
    on_read_resource=read_resource,
    on_list_prompts=list_prompts,
    on_get_prompt=get_prompt,
)

session_manager = StreamableHTTPSessionManager(app=server)
mcp_asgi_app = StreamableHTTPASGIApp(session_manager)
