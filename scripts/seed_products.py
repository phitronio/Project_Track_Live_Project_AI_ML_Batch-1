"""Load sample products into the database. Safe to run more than once."""

import asyncio
import json
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.db.session import SessionLocal, engine
from app.modules.catalog.models import Product

DATA_FILE = Path(__file__).parent / "data" / "products.json"


async def main() -> None:
    rows = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    async with SessionLocal() as session:
        stmt = (
            insert(Product)
            .values(rows)
            .on_conflict_do_nothing(index_elements=["slug"])
            .returning(Product.slug)
        )
        inserted = (await session.execute(stmt)).scalars().all()
        await session.commit()

        total = await session.scalar(select(func.count()).select_from(Product))

    print(f"Inserted {len(inserted)} new products. Total in catalog: {total}.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
