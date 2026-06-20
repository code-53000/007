from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.schemas.user import UserSimple


class FoodBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    category: str = "其他"
    quantity: float = Field(default=1.0, gt=0)
    unit: str = "份"
    box_id: int
    expiry_days: int = Field(default=7, ge=1, le=3650)
    notes: Optional[str] = None


class FoodCreate(FoodBase):
    stored_at: Optional[datetime] = None


class FoodUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    box_id: Optional[int] = None
    expiry_days: Optional[int] = None
    notes: Optional[str] = None


class FoodCleanup(BaseModel):
    note: Optional[str] = None


class FoodResponse(FoodBase):
    id: int
    owner_id: int
    stored_at: datetime
    is_cleaned: bool
    cleaned_at: Optional[datetime] = None
    cleaned_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    owner: Optional[UserSimple] = None
    expiry_date: Optional[datetime] = None
    is_expired: Optional[bool] = False
    days_until_expiry: Optional[int] = 999
    expiry_status: Optional[str] = "正常"

    class Config:
        from_attributes = True


class ExpiryStats(BaseModel):
    total: int = 0
    normal: int = 0
    warning: int = 0
    soon: int = 0
    expired: int = 0


class BulkCleanupRequest(BaseModel):
    food_ids: List[int] = Field(..., min_length=1)
    note: Optional[str] = None


class BulkCleanupResponse(BaseModel):
    success: int = 0
    failed: int = 0
    failed_ids: List[int] = []
