from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import or_

from app.modules.catalog.models import Product
from app.modules.catalog.schemas import ProductFilters, SortOption

SORTS = {
    SortOption.NEWEST: Product.created_at.desc(),
    SortOption.PRICE_ASC: Product.price.asc(),
    SortOption.PRICE_DESC: Product.price.desc(),
    SortOption.NAME: Product.name.asc(),
}


class ProductRepository:
    """All SQL for products lives here"""

    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    async def add(self, product: Product) -> Product:
        self.db_session.add(product)
        return await self.save(product)

    async def save(self, product: Product) -> Product:
        await self.db_session.flush()
        await self.db_session.refresh(product)
        return product

    async def get_by_slug(self, slug: str) -> Product | None:
        stmt = select(Product).where(Product.slug == slug, Product.is_active.is_(True))
        return await self.db_session.scalar(stmt)

    async def exists_by_slug(self, slug: str) -> bool:
        stmt = select(Product.id).where(
            Product.slug == slug, Product.is_active.is_(True)
        )
        return await self.db_session.scalar(stmt) is not None

    def _filtered(self, f: ProductFilters) -> Select:
        stmt = select(Product).where(Product.is_active.is_(True))
        if f.q:
            pattern = f"%{f.q}%"
            stmt = stmt.where(
                or_(
                    (Product.name.ilike(pattern)),
                    (Product.description.ilike(pattern)),
                    (Product.brand.ilike(pattern)),
                )
            )
        if f.category:
            stmt = stmt.where(Product.category == f.category)
        if f.brand:
            stmt = stmt.where(func.lower(Product.brand) == f.brand.lower())
        if f.min_price is not None:
            stmt = stmt.where(Product.price >= f.min_price)
        if f.max_price is not None:
            stmt = stmt.where(Product.price <= f.max_price)
        if f.in_stock is True:
            stmt = stmt.where(Product.stock > 0)
        elif f.in_stock is False:
            stmt = stmt.where(Product.stock == 0)
        return stmt

    async def search(self, f: ProductFilters) -> tuple[list[Product], int]:
        base = self._filtered(f)
        total = await self.db_session.scalar(
            select(func.count()).select_from(base.subquery())
        )
        stmt = (
            base.order_by(SORTS[f.sort], Product.id)
            .offset((f.page - 1) * f.page_size)
            .limit(f.page_size)
        )
        items = (await self.db_session.scalars(stmt)).all()
        return list(items), total or 0
