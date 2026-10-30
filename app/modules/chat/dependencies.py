from typing import Annotated

from fastapi import Depends

from app.integrations.llm.dependencies import LLMDep
from app.modules.catalog.dependencies import ProductServiceDep
from app.modules.chat.services import ChatService
from app.modules.knowledge.dependencies import KnowledgeServiceDep


def get_chat_service(
    llm: LLMDep,
    products: ProductServiceDep,
    knowledge: KnowledgeServiceDep,
) -> ChatService:
    return ChatService(llm, products, knowledge)


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
