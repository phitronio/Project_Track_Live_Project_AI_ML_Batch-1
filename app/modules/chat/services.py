from typing import Any

from app.integrations.llm.base import ChatMessage, LLMProvider
from app.modules.catalog.services import ProductService
from app.modules.chat.prompts import ASSISTANT_PROMPT
from app.modules.chat.schemas import AssistantResponse, ConversationRequest
from app.modules.chat.tools import TOOLS, execute_tool
from app.modules.knowledge.services import KnowledgeService


class ChatService:
    def __init__(
        self,
        llm: LLMProvider,
        products: ProductService,
        knowledge: KnowledgeService,
    ) -> None:
        self.llm = llm
        self.products = products
        self.knowledge = knowledge

    async def reply(self, data: ConversationRequest) -> AssistantResponse:
        messages = [*data.history, ChatMessage(role="user", content=data.content)]
        result = await self.llm.chat_with_tools(
            system=ASSISTANT_PROMPT,
            messages=messages,
            tools=TOOLS,
            run_tool=self.run_tool,
        )
        return AssistantResponse(reply=result.text, tool_calls=result.tool_calls)

    async def run_tool(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        return await execute_tool(self.products, self.knowledge, name, args)
