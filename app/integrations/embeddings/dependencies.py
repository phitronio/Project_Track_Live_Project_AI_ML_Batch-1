from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import get_settings
from app.integrations.embeddings.client import EmbeddingClient


@lru_cache
def get_embedding_client() -> EmbeddingClient:
    return EmbeddingClient(base_url=get_settings().EMBEDDINGS_URL)


EmbeddingDep = Annotated[EmbeddingClient, Depends(get_embedding_client)]
