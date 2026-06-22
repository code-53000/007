from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy import text
import asyncio

from app.config import settings
from app.database import init_db
from app.routers import api_router


async def _auto_cleanup_expired_boxes():
    from app.database import SessionLocal
    from app.models import Box, Food
    from app.core import log_operation
    from datetime import datetime

    while True:
        await asyncio.sleep(3600)
        try:
            db = SessionLocal()
            now = datetime.utcnow()
            private_boxes = db.query(Box).filter(Box.is_public == False).all()
            released_count = 0
            for box in private_boxes:
                computed = box.box_status
                if computed == "released":
                    for food in box.foods:
                        if not food.is_cleaned:
                            food.is_cleaned = True
                            food.cleaned_at = now
                            food.cleaned_by = box.owner_id
                    db.delete(box)
                    released_count += 1
            if released_count > 0:
                db.commit()
            db.close()
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    task = asyncio.create_task(_auto_cleanup_expired_boxes())
    yield
    task.cancel()


app = FastAPI(
    title=settings.app_name,
    description="合租房冰箱管理系统 - Fresh Log API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    detail = str(exc) if str(exc) else "服务器内部错误"
    if len(detail) > 200:
        detail = detail[:200] + "..."
    return JSONResponse(
        status_code=500,
        content={"detail": detail, "error_type": exc.__class__.__name__},
    )


app.include_router(api_router)


@app.get("/", tags=["根路径"])
async def root():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    from app.database import SessionLocal
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)}
        )
