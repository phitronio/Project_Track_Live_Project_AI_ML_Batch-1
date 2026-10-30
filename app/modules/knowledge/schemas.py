import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SearchMode(str, Enum):
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class Source(str, Enum):
    POLICY = "policy"
    PRODUCT = "product"


class SearchHit(BaseModel):
    source: str
    title: str
    content: str
    score: float


class ChunkCreate(BaseModel):
    source: Source
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class ChunkUpdate(BaseModel):
    """Every field is optional: only what the client sends is changed"""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, min_length=1)


class ChunkRead(BaseModel):
    id: uuid.UUID
    source: Source
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChunkFilters(BaseModel):
    """Query parameters for GET /knowledge"""

    source: Source | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class ChunkPage(BaseModel):
    items: list[ChunkRead]
    total: int
    page: int
    page_size: int


class IngestResult(BaseModel):
    policies: int
    products: int
    total: int
