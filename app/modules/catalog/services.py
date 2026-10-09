from app.core.exceptions.errors import ConflictError, NotFoundError
from app.modules.catalog.models import Product
from app.modules.catalog.repositories import ProductRepository
from app.modules.catalog.schemas import (
    Page,
    ProductCreate,
    ProductFilters,
    ProductRead,
    ProductUpdate,
)


def to_read(product: Product) -> ProductRead:
    return ProductRead.model_validate(product)


class ProductService:
    """Business rules"""

    def __init__(self, repo: ProductRepository) -> None:
        self.repo = repo

    async def create_product(self, data: ProductCreate) -> ProductRead:
        if await self.repo.exists_by_slug(data.slug):
            raise ConflictError("Product", data.slug)
        product = await self.repo.add(Product(**data.model_dump()))
        return to_read(product)

    async def get_product(self, slug: str) -> ProductRead:
        product = await self.repo.get_by_slug(slug)
        if product is None:
            raise NotFoundError("Product", slug)
        return to_read(product)

    async def get_all_products(self, filters: ProductFilters) -> Page:
        if (
            filters.min_price
            and filters.max_price
            and filters.min_price > filters.max_price
        ):
            filters.min_price, filters.max_price = filters.max_price, filters.min_price
        items, total = await self.repo.search(filters)
        return Page(
            items=[to_read(p) for p in items],
            total=total,
            page=filters.page,
            page_size=filters.page_size,
        )

    async def update_product(self, slug: str, data: ProductUpdate) -> ProductRead:
        product = await self.repo.get_by_slug(slug)
        if product is None:
            raise NotFoundError("Product", slug)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await self.repo.save(product)
        return to_read(product)

    async def archive_product(self, slug: str) -> None:
        product = await self.repo.get_by_slug(slug)
        if product is None:
            raise NotFoundError("Product", slug)
        product.is_active = False
