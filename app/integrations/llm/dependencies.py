from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import get_settings
from app.integrations.llm.base import LLMProvider
from app.integrations.llm.gemini import GeminiProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    return GeminiProvider(
        api_key=settings.GEMINI_API_KEY.get_secret_value(),
        model=settings.GEMINI_MODEL,
    )


LLMDep = Annotated[LLMProvider, Depends(get_llm_provider)]
