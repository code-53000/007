from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    nickname: str = Field(..., min_length=1, max_length=50)
    avatar_color: str = "#1989fa"
    room_number: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=4, max_length=50)


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_color: Optional[str] = None
    room_number: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserSimple(BaseModel):
    id: int
    nickname: str
    avatar_color: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None
