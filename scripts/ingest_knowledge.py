"""Cut the store policies and the products into chunks, embed them, store them.

Safe to run more than once: it replaces every chunk.
"""

import asyncio
import logging

from app.db.session import SessionLocal, engine
from app.integrations.embeddings.dependencies import get_embedding_client
from app.modules.knowledge.repositories import KnowledgeRepository
from app.modules.knowledge.services import KnowledgeService


def show_item(source: str, title: str) -> None:
    print(f"\n{source:<8} {title}")


async def main() -> None:
    async with SessionLocal() as session:
        service = KnowledgeService(KnowledgeRepository(session), get_embedding_client())
        result = await service.ingest_all(on_item=show_item)
        await session.commit()

    print(f"\nStored {result.total} chunks.")
    await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(main())
