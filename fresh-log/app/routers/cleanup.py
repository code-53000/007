from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, CleanupRecord, Food
from app.schemas import CleanupRecordResponse, UserSimple
from app.core import get_current_user

router = APIRouter(prefix="/api/cleanup", tags=["清理记录"])


@router.get("/records", response_model=List[CleanupRecordResponse], summary="获取清理记录列表")
def list_cleanup_records(
    operator_id: Optional[int] = None,
    days: Optional[int] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(CleanupRecord)
    if operator_id is not None:
        query = query.filter(CleanupRecord.operator_id == operator_id)
    if days is not None:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(CleanupRecord.created_at >= cutoff)

    records = query.order_by(CleanupRecord.created_at.desc()).limit(limit).all()
    result = []
    for r in records:
        data = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        data["operator"] = UserSimple(
            id=r.operator.id,
            nickname=r.operator.nickname,
            avatar_color=r.operator.avatar_color,
        ) if r.operator else None
        result.append(CleanupRecordResponse.model_validate(data))
    return result


@router.get("/stats", summary="清理统计数据")
def cleanup_stats(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cutoff = datetime.utcnow() - timedelta(days=days)
    records = db.query(CleanupRecord).filter(CleanupRecord.created_at >= cutoff).all()

    total_cleanups = len(records)
    by_operator = {}
    for r in records:
        uid = r.operator_id
        if uid not in by_operator:
            by_operator[uid] = {
                "count": 0,
                "user": {
                    "id": r.operator.id,
                    "nickname": r.operator.nickname,
                    "avatar_color": r.operator.avatar_color,
                } if r.operator else None,
            }
        by_operator[uid]["count"] += 1

    expired_cleaned = 0
    for r in records:
        food = db.query(Food).filter(Food.id == r.food_id).first()
        if food and food.is_expired:
            expired_cleaned += 1

    return {
        "period_days": days,
        "total_cleanups": total_cleanups,
        "expired_cleaned": expired_cleaned,
        "by_operator": sorted(by_operator.values(), key=lambda x: x["count"], reverse=True),
    }


@router.get("/records/{record_id}", response_model=CleanupRecordResponse, summary="获取单条清理记录")
def get_cleanup_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(CleanupRecord).filter(CleanupRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="清理记录不存在")

    data = {c.name: getattr(record, c.name) for c in record.__table__.columns}
    data["operator"] = UserSimple(
        id=record.operator.id,
        nickname=record.operator.nickname,
        avatar_color=record.operator.avatar_color,
    ) if record.operator else None
    return CleanupRecordResponse.model_validate(data)
