from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.integrations.llm.base import ChatMessage
from app.integrations.llm.dependencies import LLMDep
from app.modules.chat.dependencies import ChatServiceDep
from app.modules.chat.prompts import SYSTEM_PROMPT

from app.modules.chat.schemas import (
    ChatRequest,
    ChatMessage,
    ChatResponse,
    ConversationRequest,
    AssistantResponse
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/basic")
async def basic_call(llm: LLMDep) -> dict[str, str]:
    messages = [
        ChatMessage(
            role="user", content="Tell me a joke."
        )
    ]
    reply = await llm.chat(system="", messages=messages)
    return {"reply": reply}


@router.post("/user", response_model=ChatResponse)
async def user_call(data: ChatRequest, llm: LLMDep) -> ChatResponse:
    messages = [ChatMessage(role="user", content=data.content)]
    reply = await llm.chat(system="", messages=messages)
    return ChatResponse(reply=reply)


@router.post("/system", response_model=ChatResponse)
async def system_call(data: ChatRequest, llm: LLMDep) -> ChatResponse:
    messages = [ChatMessage(role="user", content=data.content)]
    reply = await llm.chat(system=SYSTEM_PROMPT, messages=messages)
    return ChatResponse(reply=reply)


@router.post("/turns", response_model=ChatResponse)
async def turns_call(data: ConversationRequest, llm: LLMDep) -> ChatResponse:
    messages = [*data.history, ChatMessage(role="user", content=data.content)]
    reply = await llm.chat(system=SYSTEM_PROMPT, messages=messages)
    return ChatResponse(reply=reply)


@router.post("", response_model=AssistantResponse)
async def chat(data: ConversationRequest, service: ChatServiceDep) -> AssistantResponse:
    return await service.reply(data)