import logging
from google import genai
from google.genai import errors, types

from app.core.exceptions.errors import LLMUnavailableError
from app.integrations.llm.base import (
    ChatMessage,
    LLMReply,
    ToolRunner,
    ToolSpec
)

ROLES = {"user": "user", "assistant": "model"}  # Gemini calls the assistant "model"

MAX_TOOL_ROUNDS = 5

logger = logging.getLogger("uvicorn.error")

def to_contents(messages: list[ChatMessage]) -> list[types.Content]:
    return [
        types.Content(role=ROLES[m.role], parts=[types.Part.from_text(text=m.content)])
        for m in messages
    ]
    
def to_gemini_tools(tools: list[ToolSpec]) -> list[types.Tool]:
    declarations = [
        types.FunctionDeclaration(
            name=t.name, description=t.description, parameters_json_schema=t.parameters
        )
        for t in tools
    ]
    return [types.Tool(function_declarations=declarations)]

def describe_call(name: str, args: dict) -> str:
    return f"{name}({', '.join(f'{k}={v!r}' for k, v in args.items())})"
    
class GeminiProvider:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def chat(self, system: str, messages: list[ChatMessage]) -> str:
        contents = [
            types.Content(
                role=ROLES[m.role], parts=[types.Part.from_text(text=m.content)]
            )
            for m in messages
        ]
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=system),
            )
        except errors.APIError as exc:
            raise LLMUnavailableError(str(exc)) from exc
        return response.text or ""
    
    async def chat_with_tools(
        self,
        system: str,
        messages: list[ChatMessage],
        tools: list[ToolSpec],
        run_tool: ToolRunner,
    ) -> LLMReply:
        contents = to_contents(messages)
        config = types.GenerateContentConfig(
            system_instruction=system, tools=to_gemini_tools(tools)
        )
        tool_calls: list[str] = []

        # =====================================================================
        # ASK THE MODEL. IF IT ANSWERS WITH TEXT, WE'RE DONE. IF IT ASKS FOR
        # TOOLS, RUN THEM, SEND BACK THE RESULTS, AND ASK AGAIN.
        # =====================================================================
        for round_no in range(1, MAX_TOOL_ROUNDS + 1):
            try:
                response = await self.client.aio.models.generate_content(
                    model=self.model, contents=contents, config=config
                )
            except errors.APIError as exc:
                raise LLMUnavailableError(str(exc)) from exc

            calls = response.function_calls or []
            if not calls:
                # NO TOOL REQUESTED: THIS IS THE FINAL ANSWER
                logger.info("[round %s] model answered with text", round_no)
                return LLMReply(text=response.text or "", tool_calls=tool_calls)

            # KEEP THE MODEL'S TURN EXACTLY AS IT CAME BACK: IT CARRIES GEMINI'S
            # "THOUGHT SIGNATURES", AND GEMINI REJECTS THE NEXT CALL WITHOUT THEM.
            contents.append(response.candidates[0].content)

            # RUN EVERY TOOL IT ASKED FOR (OUR CODE, OUR DATABASE), COLLECT RESULTS
            results = []
            for call in calls:
                args = dict(call.args or {})
                tool_calls.append(describe_call(call.name, args))
                logger.info("[round %s] model asked for %s", round_no, tool_calls[-1])
                result = await run_tool(call.name, args)
                results.append(
                    types.Part.from_function_response(name=call.name, response=result)
                )
            contents.append(types.Content(role="user", parts=results))

        return LLMReply(
            text="Sorry, I couldn't finish that. Please ask in a simpler way.",
            tool_calls=tool_calls,
        )
