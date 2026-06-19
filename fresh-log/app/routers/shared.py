from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, CommonSeasoning, SpaceNotice, Box
from app.schemas import (
    CommonSeasoningCreate, CommonSeasoningUpdate, CommonSeasoningResponse,
    SpaceNoticeCreate, SpaceNoticeUpdate, SpaceNoticeResponse, UserSimple
)
from app.core import get_current_user, log_operation, format_detail

router = APIRouter(tags=["共享空间"])

seasoning_router = APIRouter(prefix="/api/seasonings", tags=["公共调料"])
space_router = APIRouter(prefix="/api/space-notices", tags=["空间预告"])


@seasoning_router.get("", response_model=List[CommonSeasoningResponse], summary="获取公共调料列表")
def list_seasonings(
    include_depleted: bool = False,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(CommonSeasoning)
    if not include_depleted:
        query = query.filter(CommonSeasoning.is_depleted == False)
    if category is not None:
        query = query.filter(CommonSeasoning.category == category)

    items = query.order_by(CommonSeasoning.created_at.desc()).all()
    result = []
    for s in items:
        data = {c.name: getattr(s, c.name) for c in s.__table__.columns}
        data["adder"] = UserSimple(
            id=s.adder.id, nickname=s.adder.nickname,
            avatar_color=s.adder.avatar_color,
        ) if s.adder else None
        result.append(CommonSeasoningResponse.model_validate(data))
    return result


@seasoning_router.post("", response_model=CommonSeasoningResponse, summary="添加公共调料")
def create_seasoning(
    data: CommonSeasoningCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    item = CommonSeasoning(
        **data.model_dump(),
        added_by=current_user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    log_operation(db, current_user, "create_seasoning", "seasoning", item.id,
                  format_detail(name=item.name, category=item.category),
                  ip_address=request.client.host if request else None)

    resp = {c.name: getattr(item, c.name) for c in item.__table__.columns}
    resp["adder"] = UserSimple(
        id=current_user.id, nickname=current_user.nickname,
        avatar_color=current_user.avatar_color,
    )
    return CommonSeasoningResponse.model_validate(resp)


@seasoning_router.put("/{item_id}", response_model=CommonSeasoningResponse, summary="更新调料信息")
def update_seasoning(
    item_id: int,
    data: CommonSeasoningUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(CommonSeasoning).filter(CommonSeasoning.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="调料不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)

    log_operation(db, current_user, "update_seasoning", "seasoning", item.id,
                  format_detail(**update_data))

    resp = {c.name: getattr(item, c.name) for c in item.__table__.columns}
    resp["adder"] = UserSimple(
        id=item.adder.id, nickname=item.adder.nickname,
        avatar_color=item.adder.avatar_color,
    ) if item.adder else None
    return CommonSeasoningResponse.model_validate(resp)


@seasoning_router.get("/{item_id}", response_model=CommonSeasoningResponse, summary="获取单个调料详情")
def get_seasoning(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(CommonSeasoning).filter(CommonSeasoning.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="调料不存在")

    resp = {c.name: getattr(item, c.name) for c in item.__table__.columns}
    resp["adder"] = UserSimple(
        id=item.adder.id, nickname=item.adder.nickname,
        avatar_color=item.adder.avatar_color,
    ) if item.adder else None
    return CommonSeasoningResponse.model_validate(resp)


@seasoning_router.delete("/{item_id}", summary="删除调料")
def delete_seasoning(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(CommonSeasoning).filter(CommonSeasoning.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="调料不存在")

    log_operation(db, current_user, "delete_seasoning", "seasoning", item.id,
                  format_detail(name=item.name))

    db.delete(item)
    db.commit()
    return {"message": "删除成功"}


@space_router.get("", response_model=List[SpaceNoticeResponse], summary="获取空间预告列表")
def list_space_notices(
    include_freed: bool = False,
    user_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(SpaceNotice)
    if not include_freed:
        query = query.filter(SpaceNotice.is_freed == False)
    if user_id is not None:
        query = query.filter(SpaceNotice.user_id == user_id)

    items = query.order_by(SpaceNotice.free_up_date.asc()).all()
    result = []
    for n in items:
        data = {c.name: getattr(n, c.name) for c in n.__table__.columns}
        data["user"] = UserSimple(
            id=n.user.id, nickname=n.user.nickname,
            avatar_color=n.user.avatar_color,
        ) if n.user else None
        result.append(SpaceNoticeResponse.model_validate(data))
    return result


@space_router.post("", response_model=SpaceNoticeResponse, summary="发布空间预告")
def create_space_notice(
    data: SpaceNoticeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    if data.box_id is not None:
        box = db.query(Box).filter(Box.id == data.box_id).first()
        if not box:
            raise HTTPException(status_code=400, detail="指定的格子不存在")

    item = SpaceNotice(
        **data.model_dump(),
        user_id=current_user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    log_operation(db, current_user, "create_space_notice", "space_notice", item.id,
                  format_detail(free_up_date=str(item.free_up_date), box_id=item.box_id),
                  ip_address=request.client.host if request else None)

    resp = {c.name: getattr(item, c.name) for c in item.__table__.columns}
    resp["user"] = UserSimple(
        id=current_user.id, nickname=current_user.nickname,
        avatar_color=current_user.avatar_color,
    )
    return SpaceNoticeResponse.model_validate(resp)


@space_router.put("/{notice_id}", response_model=SpaceNoticeResponse, summary="更新空间预告")
def update_space_notice(
    notice_id: int,
    data: SpaceNoticeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(SpaceNotice).filter(SpaceNotice.id == notice_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="预告不存在")

    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有发布者可以修改")

    update_data = data.model_dump(exclude_unset=True)

    if "box_id" in update_data and update_data["box_id"] is not None:
        box = db.query(Box).filter(Box.id == update_data["box_id"]).first()
        if not box:
            raise HTTPException(status_code=400, detail="指定的格子不存在")

    for key, value in update_data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)

    log_operation(db, current_user, "update_space_notice", "space_notice", item.id,
                  format_detail(**update_data))

    resp = {c.name: getattr(item, c.name) for c in item.__table__.columns}
    resp["user"] = UserSimple(
        id=item.user.id, nickname=item.user.nickname,
        avatar_color=item.user.avatar_color,
    ) if item.user else None
    return SpaceNoticeResponse.model_validate(resp)


@space_router.get("/{notice_id}", response_model=SpaceNoticeResponse, summary="获取单个空间预告详情")
def get_space_notice(
    notice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(SpaceNotice).filter(SpaceNotice.id == notice_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="预告不存在")

    resp = {c.name: getattr(item, c.name) for c in item.__table__.columns}
    resp["user"] = UserSimple(
        id=item.user.id, nickname=item.user.nickname,
        avatar_color=item.user.avatar_color,
    ) if item.user else None
    return SpaceNoticeResponse.model_validate(resp)


@space_router.delete("/{notice_id}", summary="删除空间预告")
def delete_space_notice(
    notice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(SpaceNotice).filter(SpaceNotice.id == notice_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="预告不存在")

    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有发布者可以删除")

    log_operation(db, current_user, "delete_space_notice", "space_notice", item.id)

    db.delete(item)
    db.commit()
    return {"message": "删除成功"}


router.include_router(seasoning_router)
router.include_router(space_router)
