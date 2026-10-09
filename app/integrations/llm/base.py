from typing import Literal, Protocol

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class LLMProvider(Protocol):
    async def chat(self, system: str, messages: list[ChatMessage]) -> str: ...
