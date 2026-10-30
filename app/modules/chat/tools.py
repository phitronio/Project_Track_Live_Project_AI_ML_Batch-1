from typing import Any

import httpx
from pydantic import ValidationError

from app.core.exceptions.errors import NotFoundError
from app.integrations.llm.base import ToolSpec
from app.modules.catalog.schemas import ProductFilters, ProductRead
from app.modules.catalog.services import ProductService
from app.modules.knowledge.schemas import SearchMode, Source
from app.modules.knowledge.services import KnowledgeService

SEARCH_PRODUCTS = ToolSpec(
    name="search_products",
    description=(
        "Search Kinbo's catalog. Returns up to 10 products with slug, name, price in BDT "
        "and whether each is in stock. Call it before recommending any product."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "ONE keyword from a name, brand or description, "
                "e.g. 'gaming' or 'Samsung'. Leave it out to list a whole category.",
            },
            "category": {
                "type": "string",
                "enum": ["phone", "laptop", "tablet", "accessory"],
            },
            "max_price": {
                "type": "number",
                "description": "The customer's budget in BDT.",
            },
        },
    },
)

GET_PRODUCT_DETAILS = ToolSpec(
    name="get_product_details",
    description=(
        "Full specs, description, warranty and live stock of one product. "
        "Use a slug returned by search_products."
    ),
    parameters={
        "type": "object",
        "properties": {"slug": {"type": "string"}},
        "required": ["slug"],
    },
)

SEARCH_POLICIES = ToolSpec(
    name="search_policies",
    description=(
        "Search Kinbo's store policies: payment, cash on delivery, EMI, delivery, "
        "order status, cancelling, returns, refunds, warranty, support and more. "
        "Returns the 3 most relevant policy sections."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "What to look for, as a short question in English, "
                "e.g. 'can I return an opened phone'.",
            },
        },
        "required": ["query"],
    },
)

TOOLS = [SEARCH_PRODUCTS, GET_PRODUCT_DETAILS, SEARCH_POLICIES]


def summary(p: ProductRead) -> dict[str, Any]:
    return {
        "slug": p.slug,
        "name": p.name,
        "price_bdt": str(p.price),
        "in_stock": p.in_stock,
    }


async def execute_tool(
    products: ProductService,
    knowledge: KnowledgeService,
    name: str,
    args: dict[str, Any],
) -> dict[str, Any]:
    try:
        if name == "search_policies":
            hits = await knowledge.search(
                args["query"], SearchMode.HYBRID, Source.POLICY, limit=3
            )
            return {"sections": [{"title": h.title, "text": h.content} for h in hits]}
        if name == "search_products":
            filters = ProductFilters(
                q=args.get("query") or None,
                category=args.get("category"),
                max_price=args.get("max_price"),
                page_size=10,
            )
            page = await products.get_all_products(filters)
            return {"products": [summary(p) for p in page.items]}
        if name == "get_product_details":
            product = await products.get_product(args["slug"])
            return product.model_dump(mode="json", exclude={"id"})
        return {"error": f"Unknown tool: {name}"}
    except (ValidationError, NotFoundError, KeyError, httpx.HTTPError) as exc:
        return {"error": str(exc)}
