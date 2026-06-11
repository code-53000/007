from sqlalchemy.orm import Session
from app.models import OperationLog, User
from typing import Optional


def log_operation(
    db: Session,
    user: User,
    action: str,
    target_type: str,
    target_id: Optional[int] = None,
    detail: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> OperationLog:
    log = OperationLog(
        user_id=user.id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def format_detail(**kwargs) -> str:
    return "; ".join([f"{k}={v}" for k, v in kwargs.items() if v is not None])
