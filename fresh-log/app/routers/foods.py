from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Food, Box, CleanupRecord
from app.schemas import (
    FoodCreate, FoodUpdate, FoodCleanup, FoodResponse, ExpiryStats
)
from app.core import (
    get_current_user, log_operation, format_detail,
    enrich_food_with_expiry, get_expiry_stats as calc_expiry_stats,
    get_expiry_status
)

router = APIRouter(prefix="/api/foods", tags=["食物"])


@router.get("", response_model=List[FoodResponse], summary="获取食物列表")
def list_foods(
    box_id: Optional[int] = None,
    owner_id: Optional[int] = None,
    category: Optional[str] = None,
    status: Optional[str] = Query(None, description="expired/soon/warning/normal"),
    only_active: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Food)
    if only_active:
        query = query.filter(Food.is_cleaned == False)
    if box_id is not None:
        query = query.filter(Food.box_id == box_id)
    if owner_id is not None:
        query = query.filter(Food.owner_id == owner_id)
    if category is not None:
        query = query.filter(Food.category == category)

    foods = query.order_by(Food.stored_at.desc()).all()

    result = []
    for food in foods:
        enriched = enrich_food_with_expiry(food)
        if status:
            status_map = {
                "expired": "已过期",
                "soon": "即将到期",
                "warning": "临期",
                "normal": "正常",
            }
            if enriched["expiry_status"] != status_map.get(status, ""):
                continue
        result.append(FoodResponse.model_validate(enriched))
    return result


@router.get("/{food_id}", response_model=FoodResponse, summary="获取食物详情")
def get_food(
    food_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    food = db.query(Food).filter(Food.id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="食物不存在")
    return FoodResponse.model_validate(enrich_food_with_expiry(food))


@router.post("", response_model=FoodResponse, summary="登记新食物")
def create_food(
    food_data: FoodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    box = db.query(Box).filter(Box.id == food_data.box_id).first()
    if not box:
        raise HTTPException(status_code=400, detail="指定的格子不存在")

    if box.owner_id and box.owner_id != current_user.id and not box.is_public:
        raise HTTPException(status_code=403, detail="无权使用此私有格子")

    food = Food(
        name=food_data.name,
        category=food_data.category,
        quantity=food_data.quantity,
        unit=food_data.unit,
        box_id=food_data.box_id,
        owner_id=current_user.id,
        stored_at=food_data.stored_at or datetime.utcnow(),
        expiry_days=food_data.expiry_days,
        notes=food_data.notes,
    )
    db.add(food)
    db.commit()
    db.refresh(food)

    log_operation(db, current_user, "create_food", "food", food.id,
                  format_detail(name=food.name, box_id=food.box_id,
                               expiry_days=food.expiry_days),
                  ip_address=request.client.host if request else None)

    return FoodResponse.model_validate(enrich_food_with_expiry(food))


@router.put("/{food_id}", response_model=FoodResponse, summary="更新食物信息")
def update_food(
    food_id: int,
    food_data: FoodUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    food = db.query(Food).filter(Food.id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="食物不存在")

    if food.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有食物所有者可以修改")

    if food.is_cleaned:
        raise HTTPException(status_code=400, detail="已清理的食物无法修改")

    update_data = food_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(food, key, value)

    db.commit()
    db.refresh(food)

    log_operation(db, current_user, "update_food", "food", food.id,
                  format_detail(**update_data))

    return FoodResponse.model_validate(enrich_food_with_expiry(food))


@router.post("/{food_id}/cleanup", response_model=FoodResponse, summary="标记食物已清理")
def cleanup_food(
    food_id: int,
    cleanup_data: FoodCleanup,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    food = db.query(Food).filter(Food.id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="食物不存在")

    if food.is_cleaned:
        raise HTTPException(status_code=400, detail="食物已被清理")

    food.is_cleaned = True
    food.cleaned_at = datetime.utcnow()
    food.cleaned_by = current_user.id

    record = CleanupRecord(
        food_id=food.id,
        operator_id=current_user.id,
        action="清理" if food.owner_id == current_user.id else "代清理",
        note=cleanup_data.note,
    )
    db.add(record)
    db.commit()
    db.refresh(food)

    log_operation(db, current_user, "cleanup_food", "food", food.id,
                  format_detail(name=food.name, action=record.action,
                               note=cleanup_data.note))

    return FoodResponse.model_validate(enrich_food_with_expiry(food))


@router.delete("/{food_id}", summary="删除食物记录")
def delete_food(
    food_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    food = db.query(Food).filter(Food.id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="食物不存在")

    if food.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有食物所有者可以删除")

    log_operation(db, current_user, "delete_food", "food", food.id,
                  format_detail(name=food.name))

    db.delete(food)
    db.commit()
    return {"message": "删除成功"}


@router.get("/stats/expiry", response_model=ExpiryStats, summary="获取过期统计")
def expiry_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stats = calc_expiry_stats(db)
    return ExpiryStats(**stats)


@router.get("/mine/expiring", response_model=List[FoodResponse], summary="获取我的即将过期食物")
def get_my_expiring(
    days: int = 3,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    foods = db.query(Food).filter(
        Food.owner_id == current_user.id,
        Food.is_cleaned == False
    ).all()

    result = []
    for food in foods:
        enriched = enrich_food_with_expiry(food)
        if enriched["days_until_expiry"] <= days:
            result.append(FoodResponse.model_validate(enriched))
    return sorted(result, key=lambda x: x.days_until_expiry)


@router.get("/categories", summary="获取所有食物分类")
def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from sqlalchemy import func
    categories = (
        db.query(Food.category, func.count(Food.id))
        .filter(Food.is_cleaned == False)
        .group_by(Food.category)
        .all()
    )
    default_categories = ["蔬菜", "水果", "肉类", "蛋奶", "主食", "饮料", "调料", "剩菜", "其他"]
    existing = {c[0]: c[1] for c in categories}
    result = []
    for cat in default_categories:
        result.append({"name": cat, "count": existing.get(cat, 0)})
    for cat, count in categories:
        if cat not in default_categories:
            result.append({"name": cat, "count": count})
    return result
