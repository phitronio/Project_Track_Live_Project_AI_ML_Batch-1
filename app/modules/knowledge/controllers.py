import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.modules.knowledge.dependencies import KnowledgeServiceDep
from app.modules.knowledge.schemas import (
    ChunkCreate,
    ChunkFilters,
    ChunkPage,
    ChunkRead,
    ChunkUpdate,
    IngestResult,
    SearchHit,
    SearchMode,
    Source,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/search", response_model=list[SearchHit])
async def search(
    service: KnowledgeServiceDep,
    q: Annotated[str, Query(min_length=2, max_length=200)],
    mode: SearchMode = SearchMode.HYBRID,
    source: Source | None = None,
    limit: Annotated[int, Query(ge=1, le=10)] = 3,
) -> list[SearchHit]:
    return await service.search(q, mode, source, limit)


@router.post("/ingest", response_model=IngestResult)
async def ingest(service: KnowledgeServiceDep) -> IngestResult:
    return await service.ingest_all()


@router.post("", response_model=ChunkRead, status_code=status.HTTP_201_CREATED)
async def create_chunk(data: ChunkCreate, service: KnowledgeServiceDep) -> ChunkRead:
    return await service.create_chunk(data)


@router.get("", response_model=ChunkPage)
async def list_chunks(
    filters: Annotated[ChunkFilters, Query()], service: KnowledgeServiceDep
) -> ChunkPage:
    return await service.list_chunks(filters)


@router.get("/{chunk_id}", response_model=ChunkRead)
async def get_chunk(chunk_id: uuid.UUID, service: KnowledgeServiceDep) -> ChunkRead:
    return await service.get_chunk(chunk_id)


@router.put("/{chunk_id}", response_model=ChunkRead)
async def update_chunk(
    chunk_id: uuid.UUID, data: ChunkUpdate, service: KnowledgeServiceDep
) -> ChunkRead:
    return await service.update_chunk(chunk_id, data)


@router.delete("/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chunk(chunk_id: uuid.UUID, service: KnowledgeServiceDep) -> None:
    await service.delete_chunk(chunk_id)
