from fastapi import APIRouter
from app.routers.auth import router as auth_router
from app.routers.boxes import router as boxes_router
from app.routers.foods import router as foods_router
from app.routers.cleanup import router as cleanup_router
from app.routers.shared import router as shared_router
from app.routers.logs import router as logs_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(boxes_router)
api_router.include_router(foods_router)
api_router.include_router(cleanup_router)
api_router.include_router(shared_router)
api_router.include_router(logs_router)

__all__ = ["api_router"]
