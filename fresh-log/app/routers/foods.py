from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Food, Box, CleanupRecord
from app.schemas import (
    FoodCreate, FoodUpdate, FoodCleanup, FoodResponse, ExpiryStats,
    BulkCleanupRequest, BulkCleanupResponse
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
    sort_by_expiry: bool = False,
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

    foods = query.all()

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

    if sort_by_expiry:
        result.sort(key=lambda x: x.days_until_expiry)
    else:
        result.sort(key=lambda x: x.stored_at, reverse=True)

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

    active_foods = [f for f in box.foods if not f.is_cleaned]
    used_capacity = sum(f.quantity for f in active_foods)
    if used_capacity + food_data.quantity > box.capacity:
        raise HTTPException(
            status_code=400,
            detail=f"格子容量不足，当前已用{used_capacity}份，剩余{box.capacity - used_capacity}份"
        )

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

    new_box_id = update_data.get("box_id", food.box_id)
    new_quantity = update_data.get("quantity", food.quantity)
    if new_box_id != food.box_id or new_quantity != food.quantity:
        box = db.query(Box).filter(Box.id == new_box_id).first()
        if not box:
            raise HTTPException(status_code=400, detail="指定的格子不存在")
        active_foods = [f for f in box.foods if not f.is_cleaned and f.id != food.id]
        used_capacity = sum(f.quantity for f in active_foods)
        if used_capacity + new_quantity > box.capacity:
            raise HTTPException(
                status_code=400,
                detail=f"格子容量不足，当前已用{used_capacity}份，剩余{box.capacity - used_capacity}份"
            )

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


@router.post("/bulk-cleanup", response_model=BulkCleanupResponse, summary="批量标记食物已清理")
def bulk_cleanup_foods(
    bulk_data: BulkCleanupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success_count = 0
    failed_ids = []
    now = datetime.utcnow()

    try:
        for food_id in bulk_data.food_ids:
            try:
                food = db.query(Food).filter(Food.id == food_id).first()
                if not food or food.is_cleaned:
                    failed_ids.append(food_id)
                    continue

                food.is_cleaned = True
                food.cleaned_at = now
                food.cleaned_by = current_user.id

                record = CleanupRecord(
                    food_id=food.id,
                    operator_id=current_user.id,
                    action="清理" if food.owner_id == current_user.id else "代清理",
                    note=bulk_data.note,
                )
                db.add(record)
                success_count += 1
            except Exception:
                failed_ids.append(food_id)

        db.commit()

        for food_id in bulk_data.food_ids:
            if food_id not in failed_ids:
                food = db.query(Food).filter(Food.id == food_id).first()
                if food:
                    action = "清理" if food.owner_id == current_user.id else "代清理"
                    log_operation(db, current_user, "cleanup_food", "food", food.id,
                                  format_detail(name=food.name, action=action,
                                               note=bulk_data.note))

        return BulkCleanupResponse(
            success=success_count,
            failed=len(failed_ids),
            failed_ids=failed_ids
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"批量清理失败: {str(e)}")


@router.get("/mine/list", response_model=List[FoodResponse], summary="获取我的食物列表（按临期排序）")
def get_my_foods(
    only_active: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Food).filter(Food.owner_id == current_user.id)
    if only_active:
        query = query.filter(Food.is_cleaned == False)

    foods = query.all()
    result = []
    for food in foods:
        enriched = enrich_food_with_expiry(food)
        result.append(FoodResponse.model_validate(enriched))

    result.sort(key=lambda x: x.days_until_expiry)
    return result


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
