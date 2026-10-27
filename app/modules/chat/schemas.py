from pydantic import BaseModel, Field
from app.integrations.llm.base import ChatMessage

class ChatRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str
    
class ConversationRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default=[], max_length=20)
    
class AssistantResponse(BaseModel):
    reply: str
    tool_calls: list[str] = []