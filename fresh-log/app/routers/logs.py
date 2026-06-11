from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, OperationLog
from app.schemas import OperationLogResponse, UserSimple
from app.core import get_current_user

router = APIRouter(prefix="/api/logs", tags=["操作日志"])


@router.get("", response_model=List[OperationLogResponse], summary="获取操作日志列表")
def list_operation_logs(
    user_id: Optional[int] = None,
    target_type: Optional[str] = None,
    action: Optional[str] = None,
    days: Optional[int] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(OperationLog)
    if user_id is not None:
        query = query.filter(OperationLog.user_id == user_id)
    if target_type is not None:
        query = query.filter(OperationLog.target_type == target_type)
    if action is not None:
        query = query.filter(OperationLog.action == action)
    if days is not None:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(OperationLog.created_at >= cutoff)

    logs = query.order_by(OperationLog.created_at.desc()).limit(limit).all()
    result = []
    for log in logs:
        data = {c.name: getattr(log, c.name) for c in log.__table__.columns}
        data["user"] = UserSimple(
            id=log.user.id, nickname=log.user.nickname,
            avatar_color=log.user.avatar_color,
        ) if log.user else None
        result.append(OperationLogResponse.model_validate(data))
    return result


@router.get("/summary", summary="操作日志统计摘要")
def logs_summary(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cutoff = datetime.utcnow() - timedelta(days=days)
    logs = db.query(OperationLog).filter(OperationLog.created_at >= cutoff).all()

    by_action = {}
    by_target = {}
    by_user = {}

    for log in logs:
        by_action[log.action] = by_action.get(log.action, 0) + 1
        by_target[log.target_type] = by_target.get(log.target_type, 0) + 1
        uid = log.user_id
        if uid not in by_user:
            by_user[uid] = {
                "count": 0,
                "user": {
                    "id": log.user.id,
                    "nickname": log.user.nickname,
                    "avatar_color": log.user.avatar_color,
                } if log.user else None,
            }
        by_user[uid]["count"] += 1

    return {
        "period_days": days,
        "total_ops": len(logs),
        "by_action": by_action,
        "by_target_type": by_target,
        "top_users": sorted(by_user.values(), key=lambda x: x["count"], reverse=True)[:5],
    }


@router.get("/actions", summary="获取所有操作类型")
def get_action_types(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from sqlalchemy import func
    actions = (
        db.query(OperationLog.action, func.count(OperationLog.id))
        .group_by(OperationLog.action)
        .all()
    )
    return [{"action": a[0], "count": a[1]} for a in actions]
