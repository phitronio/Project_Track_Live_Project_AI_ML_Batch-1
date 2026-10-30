from typing import Annotated

from fastapi import Depends

from app.db.session import SessionDep
from app.integrations.embeddings.dependencies import EmbeddingDep
from app.modules.knowledge.repositories import KnowledgeRepository
from app.modules.knowledge.services import KnowledgeService


def get_knowledge_repository(session: SessionDep) -> KnowledgeRepository:
    return KnowledgeRepository(session)


KnowledgeRepositoryDep = Annotated[
    KnowledgeRepository, Depends(get_knowledge_repository)
]


def get_knowledge_service(
    repo: KnowledgeRepositoryDep, embedder: EmbeddingDep
) -> KnowledgeService:
    return KnowledgeService(repo, embedder)


KnowledgeServiceDep = Annotated[KnowledgeService, Depends(get_knowledge_service)]
