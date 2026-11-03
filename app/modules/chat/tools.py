from decimal import Decimal
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

COMPARE_PRODUCTS = ToolSpec(
    name="compare_products",
    description=(
        "Compare 2 to 4 products side by side: price in BDT, warranty, stock and specs. "
        "Use slugs returned by search_products. Use it when the customer is choosing "
        "between specific products."
    ),
    parameters={
        "type": "object",
        "properties": {
            "slugs": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 2,
                "maxItems": 4,
            },
        },
        "required": ["slugs"],
    },
)

FIND_ALTERNATIVES = ToolSpec(
    name="find_alternatives",
    description=(
        "Find up to 5 in-stock products of the same category priced within 20% of a "
        "given product, closest price first. Use it when a product is out of stock or "
        "the customer wants something similar. Use a slug returned by search_products."
    ),
    parameters={
        "type": "object",
        "properties": {"slug": {"type": "string"}},
        "required": ["slug"],
    },
)

TOOLS = [
    SEARCH_PRODUCTS,
    GET_PRODUCT_DETAILS,
    COMPARE_PRODUCTS,
    FIND_ALTERNATIVES,
    SEARCH_POLICIES,
]


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
        if name == "find_alternatives":
            base = await products.get_product(args["slug"])
            page = await products.get_all_products(
                ProductFilters(
                    category=base.category,
                    min_price=base.price * Decimal("0.8"),
                    max_price=base.price * Decimal("1.2"),
                    in_stock=True,
                    page_size=20,
                )
            )
            similar = sorted(
                (p for p in page.items if p.slug != base.slug),
                key=lambda p: abs(p.price - base.price),
            )[:5]
            return {"alternatives": [summary(p) for p in similar]}
        if name == "compare_products":
            slugs = list(dict.fromkeys(args["slugs"]))
            if not 2 <= len(slugs) <= 4:
                return {"error": "Give between 2 and 4 different product slugs."}
            compared = [await products.get_product(slug) for slug in slugs]
            return {
                "products": [
                    {
                        "slug": p.slug,
                        "name": p.name,
                        "brand": p.brand,
                        "price_bdt": str(p.price),
                        "warranty_months": p.warranty_months,
                        "in_stock": p.in_stock,
                        "specs": p.specs,
                    }
                    for p in compared
                ]
            }
        return {"error": f"Unknown tool: {name}"}
    except (ValidationError, NotFoundError, KeyError, httpx.HTTPError) as exc:
        return {"error": str(exc)}
