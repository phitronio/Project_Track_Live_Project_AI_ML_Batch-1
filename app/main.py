from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.exceptions.handlers import register_exception_handlers
from app.db.session import SessionDep
from app.mcp.server import mcp_asgi_app, session_manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with session_manager.run():
        yield


app = FastAPI(title=get_settings().APP_NAME, lifespan=lifespan)
register_exception_handlers(app)
app.include_router(api_router)
app.add_route("/mcp", mcp_asgi_app)


@app.get("/health")
async def health(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/health/db")
async def health_db(session: SessionDep) -> dict[str, str]:
    result = await session.execute(text("SELECT version();"))
    version = result.scalar_one()

    ext = await session.execute(
        text("SELECT extname FROM pg_extension WHERE extname = 'vector';")
    )
    has_vector = ext.scalar_one_or_none() is not None

    return {
        "database": "connected",
        "version": version,
        "has_vector": "yes" if has_vector else "no",
    }
