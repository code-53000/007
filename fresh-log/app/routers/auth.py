from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, Token, UserUpdate, UserSimple
from app.core import (
    get_password_hash, authenticate_user, create_access_token,
    get_current_user, log_operation, format_detail
)
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=Token, summary="用户注册")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已被使用")

    color_palette = ["#1989fa", "#07c160", "#ff976a", "#ee0a24", "#7232dd", "#606266"]
    color_index = db.query(User).count() % len(color_palette)

    user = User(
        username=user_data.username,
        nickname=user_data.nickname,
        avatar_color=user_data.avatar_color or color_palette[color_index],
        room_number=user_data.room_number,
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_operation(db, user, "register", "user", user.id,
                  format_detail(username=user.username, nickname=user.nickname))

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    return Token(access_token=access_token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=Token, summary="用户登录")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    log_operation(db, user, "login", "user", user.id)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    return Token(access_token=access_token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
def read_current_user(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)

    log_operation(db, current_user, "update_profile", "user", current_user.id,
                  format_detail(**update_data))

    return UserResponse.model_validate(current_user)


@router.get("/roommates", response_model=list[UserSimple], summary="获取所有室友列表")
def list_roommates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    users = db.query(User).filter(User.is_active == True).all()
    return [UserSimple.model_validate(u) for u in users]
