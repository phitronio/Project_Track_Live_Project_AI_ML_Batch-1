import logging
import time

import httpx

logger = logging.getLogger("uvicorn.error")

EMBEDDING_DIM = 768

QUERY_PREFIX = "task: search result | query: "


class EmbeddingClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    async def embed(self, text: str) -> list[float]:
        preview = text[:80].replace("\n", " ")
        dots = "..." if len(text) > 80 else ""
        logger.info(f'[embedding] -> model: "{preview}{dots}"')
        started = time.perf_counter()

        async with httpx.AsyncClient(base_url=self.base_url, timeout=30) as client:
            response = await client.post("/embed", json={"inputs": text})
            response.raise_for_status()
            vector = response.json()[0]

        ms = (time.perf_counter() - started) * 1000
        first = ", ".join(str(round(n, 4)) for n in vector[:5])
        logger.info(
            f"[embedding] <- model returned {len(vector)} numbers: [{first}, ...] in {ms:.0f} ms"
        )
        return vector

    # The user query or customer question
    async def embed_query(self, question: str) -> list[float]:
        return await self.embed(QUERY_PREFIX + question)

    # Ingested information or actual corpus
    async def embed_document(self, title: str, text: str) -> list[float]:
        return await self.embed(f"title: {title} | text: {text}")
