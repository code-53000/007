from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserSimple


class CleanupRecordBase(BaseModel):
    food_id: int
    action: str
    note: Optional[str] = None


class CleanupRecordResponse(CleanupRecordBase):
    id: int
    operator_id: int
    created_at: datetime
    operator: Optional[UserSimple] = None

    class Config:
        from_attributes = True


class OperationLogBase(BaseModel):
    action: str
    target_type: str
    target_id: Optional[int] = None
    detail: Optional[str] = None


class OperationLogResponse(OperationLogBase):
    id: int
    user_id: int
    ip_address: Optional[str] = None
    created_at: datetime
    user: Optional[UserSimple] = None

    class Config:
        from_attributes = True
