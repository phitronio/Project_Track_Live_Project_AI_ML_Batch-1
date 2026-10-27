from typing import Any

from app.integrations.llm.base import ChatMessage, LLMProvider
from app.modules.catalog.services import ProductService
from app.modules.chat.prompts import ASSISTANT_PROMPT
from app.modules.chat.schemas import AssistantResponse, ConversationRequest
from app.modules.chat.tools import TOOLS, execute_tool


class ChatService:
    def __init__(self, llm: LLMProvider, products: ProductService) -> None:
        self.llm = llm
        self.products = products

    async def reply(self, data: ConversationRequest) -> AssistantResponse:
        messages = [*data.history, ChatMessage(role="user", content=data.content)]
        result = await self.llm.chat_with_tools(
            system=ASSISTANT_PROMPT,
            messages=messages,
            tools=TOOLS,
            run_tool=self.run_tool,
        )
        return AssistantResponse(reply=result.text, tool_calls=result.tool_calls)

    # THE PROVIDER CALLS THIS EVERY TIME THE MODEL ASKS FOR A TOOL
    async def run_tool(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        return await execute_tool(self.products, name, args)