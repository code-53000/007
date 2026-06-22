from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.schemas.user import UserSimple


class BoxBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    floor: int = Field(..., ge=1, le=10)
    row: int = Field(..., ge=1, le=10)
    capacity: int = Field(default=10, ge=1, le=100)
    description: Optional[str] = None
    is_public: bool = False


class BoxCreate(BoxBase):
    pass


class BoxUpdate(BaseModel):
    name: Optional[str] = None
    floor: Optional[int] = Field(None, ge=1, le=10)
    row: Optional[int] = Field(None, ge=1, le=10)
    capacity: Optional[int] = Field(None, ge=1, le=100)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    is_available: Optional[bool] = None
    claimer_id: Optional[int] = None


class BoxResponse(BoxBase):
    id: int
    owner_id: Optional[int] = None
    claimer_id: Optional[int] = None
    is_available: bool
    expires_at: Optional[datetime] = None
    status: Optional[str] = "active"
    box_status: Optional[str] = "active"
    created_at: datetime
    updated_at: datetime
    owner: Optional[UserSimple] = None
    claimer: Optional[UserSimple] = None
    food_count: Optional[int] = 0
    used_capacity: Optional[int] = 0

    class Config:
        from_attributes = True


class BoxWithFoods(BoxResponse):
    foods: List = []
