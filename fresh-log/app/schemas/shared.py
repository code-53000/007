from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from app.schemas.user import UserSimple


class CommonSeasoningBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    brand: Optional[str] = None
    category: str = "调味"
    quantity: Optional[str] = None
    location_note: Optional[str] = None
    expiry_date: Optional[date] = None


class CommonSeasoningCreate(CommonSeasoningBase):
    pass


class CommonSeasoningUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[str] = None
    location_note: Optional[str] = None
    expiry_date: Optional[date] = None
    is_depleted: Optional[bool] = None


class CommonSeasoningResponse(CommonSeasoningBase):
    id: int
    added_by: Optional[int] = None
    is_depleted: bool
    created_at: datetime
    updated_at: datetime
    adder: Optional[UserSimple] = None

    class Config:
        from_attributes = True


class SpaceNoticeBase(BaseModel):
    box_id: Optional[int] = None
    free_up_date: date
    description: Optional[str] = None
    space_size: Optional[str] = None


class SpaceNoticeCreate(SpaceNoticeBase):
    pass


class SpaceNoticeUpdate(BaseModel):
    free_up_date: Optional[date] = None
    description: Optional[str] = None
    space_size: Optional[str] = None
    is_freed: Optional[bool] = None


class SpaceNoticeResponse(SpaceNoticeBase):
    id: int
    user_id: int
    is_freed: bool
    created_at: datetime
    user: Optional[UserSimple] = None

    class Config:
        from_attributes = True
