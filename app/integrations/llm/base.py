from typing import Literal, Protocol, Any
from collections.abc import Awaitable, Callable

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]
    
ToolRunner = Callable[[str, dict[str, Any]], Awaitable[dict[str, Any]]]

class LLMReply(BaseModel):
    text: str
    tool_calls: list[str] = []
    
class LLMProvider(Protocol):
    async def chat(self, system: str, messages: list[ChatMessage]) -> str: ...
    
    async def chat_with_tools(
        self,
        system: str,
        messages: list[ChatMessage],
        tools: list[ToolSpec],
        run_tool: ToolRunner,
    ) -> LLMReply: ...