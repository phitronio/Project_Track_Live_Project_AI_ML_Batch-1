from fastapi.routing import APIRouter

from app.modules.catalog.controllers import router as product_router
from app.modules.chat.controllers import router as chat_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(product_router)
api_router.include_router(chat_router)
