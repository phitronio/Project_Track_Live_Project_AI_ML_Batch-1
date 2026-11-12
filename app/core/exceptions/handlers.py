from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions.errors import (
    ConflictError,
    ForbiddenError,
    LLMUnavailableError,
    NotFoundError,
    UnauthorizedError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ConflictError)
    async def conflict(_: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(LLMUnavailableError)
    async def llm_unavailable(_: Request, exc: LLMUnavailableError) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"detail": "The assistant is unavailable. Try again later."},
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized(_: Request, exc: UnauthorizedError) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden(_: Request, exc: ForbiddenError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": str(exc)})
