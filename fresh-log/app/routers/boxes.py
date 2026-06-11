from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Box, Food
from app.schemas import BoxCreate, BoxUpdate, BoxResponse, BoxWithFoods
from app.core import get_current_user, log_operation, format_detail, enrich_food_with_expiry

router = APIRouter(prefix="/api/boxes", tags=["冰箱格子"])


@router.get("", response_model=List[BoxResponse], summary="获取所有冰箱格子列表")
def list_boxes(
    floor: Optional[int] = None,
    is_public: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Box)
    if floor is not None:
        query = query.filter(Box.floor == floor)
    if is_public is not None:
        query = query.filter(Box.is_public == is_public)

    boxes = query.order_by(Box.floor, Box.row, Box.id).all()

    result = []
    for box in boxes:
        box_dict = {c.name: getattr(box, c.name) for c in box.__table__.columns}
        box_dict["owner"] = {
            "id": box.owner.id,
            "nickname": box.owner.nickname,
            "avatar_color": box.owner.avatar_color,
        } if box.owner else None
        box_dict["claimer"] = {
            "id": box.claimer.id,
            "nickname": box.claimer.nickname,
            "avatar_color": box.claimer.avatar_color,
        } if box.claimer else None

        active_foods = [f for f in box.foods if not f.is_cleaned]
        box_dict["food_count"] = len(active_foods)
        box_dict["used_capacity"] = sum(f.quantity for f in active_foods)
        result.append(BoxResponse.model_validate(box_dict))

    return result


@router.get("/{box_id}", response_model=BoxWithFoods, summary="获取单个格子详情（含食物）")
def get_box(
    box_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        raise HTTPException(status_code=404, detail="格子不存在")

    box_dict = {c.name: getattr(box, c.name) for c in box.__table__.columns}
    box_dict["owner"] = {
        "id": box.owner.id, "nickname": box.owner.nickname,
        "avatar_color": box.owner.avatar_color,
    } if box.owner else None
    box_dict["claimer"] = {
        "id": box.claimer.id, "nickname": box.claimer.nickname,
        "avatar_color": box.claimer.avatar_color,
    } if box.claimer else None

    active_foods = [f for f in box.foods if not f.is_cleaned]
    box_dict["food_count"] = len(active_foods)
    box_dict["used_capacity"] = sum(f.quantity for f in active_foods)
    box_dict["foods"] = [enrich_food_with_expiry(f) for f in active_foods]

    return BoxWithFoods.model_validate(box_dict)


@router.post("", response_model=BoxResponse, summary="创建新的冰箱格子")
def create_box(
    box_data: BoxCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    box = Box(
        **box_data.model_dump(),
        owner_id=current_user.id,
    )
    db.add(box)
    db.commit()
    db.refresh(box)

    log_operation(db, current_user, "create_box", "box", box.id,
                  format_detail(name=box.name, floor=box.floor, row=box.row),
                  ip_address=request.client.host if request else None)

    box_dict = {c.name: getattr(box, c.name) for c in box.__table__.columns}
    box_dict["owner"] = {
        "id": current_user.id, "nickname": current_user.nickname,
        "avatar_color": current_user.avatar_color,
    }
    box_dict["claimer"] = None
    box_dict["food_count"] = 0
    box_dict["used_capacity"] = 0
    return BoxResponse.model_validate(box_dict)


@router.put("/{box_id}", response_model=BoxResponse, summary="更新格子信息")
def update_box(
    box_id: int,
    box_data: BoxUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        raise HTTPException(status_code=404, detail="格子不存在")

    if box.owner_id and box.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有格子所有者可以修改")

    update_data = box_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(box, key, value)

    db.commit()
    db.refresh(box)

    log_operation(db, current_user, "update_box", "box", box.id,
                  format_detail(**update_data))

    box_dict = {c.name: getattr(box, c.name) for c in box.__table__.columns}
    box_dict["owner"] = {
        "id": box.owner.id, "nickname": box.owner.nickname,
        "avatar_color": box.owner.avatar_color,
    } if box.owner else None
    box_dict["claimer"] = {
        "id": box.claimer.id, "nickname": box.claimer.nickname,
        "avatar_color": box.claimer.avatar_color,
    } if box.claimer else None
    active_foods = [f for f in box.foods if not f.is_cleaned]
    box_dict["food_count"] = len(active_foods)
    box_dict["used_capacity"] = sum(f.quantity for f in active_foods)

    return BoxResponse.model_validate(box_dict)


@router.delete("/{box_id}", summary="删除格子")
def delete_box(
    box_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        raise HTTPException(status_code=404, detail="格子不存在")

    if box.owner_id and box.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有格子所有者可以删除")

    active_foods = db.query(Food).filter(
        Food.box_id == box_id,
        Food.is_cleaned == False
    ).count()
    if active_foods > 0:
        raise HTTPException(status_code=400, detail="格子中还有未清理的食物，无法删除")

    log_operation(db, current_user, "delete_box", "box", box.id,
                  format_detail(name=box.name))

    db.delete(box)
    db.commit()
    return {"message": "删除成功"}


@router.get("/stats/summary", summary="获取格子占用统计")
def get_box_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_boxes = db.query(Box).count()
    public_boxes = db.query(Box).filter(Box.is_public == True).count()
    private_boxes = total_boxes - public_boxes

    occupied = db.query(Box).filter(Box.is_available == False).count()
    floors = db.query(func.distinct(Box.floor)).count()

    return {
        "total_boxes": total_boxes,
        "public_boxes": public_boxes,
        "private_boxes": private_boxes,
        "occupied_boxes": occupied,
        "available_boxes": total_boxes - occupied,
        "total_floors": floors,
    }
