from datetime import datetime, timedelta
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models import Food


EXPIRY_STATUS_NORMAL = "正常"
EXPIRY_STATUS_SOON = "即将到期"
EXPIRY_STATUS_WARNING = "临期"
EXPIRY_STATUS_EXPIRED = "已过期"


def get_expiry_status(food: Food) -> str:
    if food.is_cleaned:
        return EXPIRY_STATUS_NORMAL

    days = food.days_until_expiry
    if days < 0:
        return EXPIRY_STATUS_EXPIRED
    elif days <= 1:
        return EXPIRY_STATUS_WARNING
    elif days <= 3:
        return EXPIRY_STATUS_SOON
    else:
        return EXPIRY_STATUS_NORMAL


def get_expiry_status_color(status: str) -> str:
    color_map = {
        EXPIRY_STATUS_NORMAL: "#07c160",
        EXPIRY_STATUS_SOON: "#ff976a",
        EXPIRY_STATUS_WARNING: "#ee0a24",
        EXPIRY_STATUS_EXPIRED: "#969799",
    }
    return color_map.get(status, "#969799")


def get_expired_foods(db: Session) -> List[Food]:
    all_active = db.query(Food).filter(Food.is_cleaned == False).all()
    return [f for f in all_active if f.is_expired]


def get_soon_expired_foods(db: Session, days: int = 3) -> List[Food]:
    all_active = db.query(Food).filter(Food.is_cleaned == False).all()
    return [
        f for f in all_active
        if not f.is_expired and f.days_until_expiry <= days
    ]


def get_expiry_stats(db: Session) -> dict:
    all_active_foods = db.query(Food).filter(Food.is_cleaned == False).all()

    stats = {
        "total": len(all_active_foods),
        "normal": 0,
        "warning": 0,
        "soon": 0,
        "expired": 0,
    }

    for food in all_active_foods:
        status = get_expiry_status(food)
        if status == EXPIRY_STATUS_EXPIRED:
            stats["expired"] += 1
        elif status == EXPIRY_STATUS_WARNING:
            stats["warning"] += 1
        elif status == EXPIRY_STATUS_SOON:
            stats["soon"] += 1
        else:
            stats["normal"] += 1

    return stats


def enrich_food_with_expiry(food: Food) -> dict:
    data = {c.name: getattr(food, c.name) for c in food.__table__.columns}
    data["expiry_date"] = food.expiry_date
    data["is_expired"] = food.is_expired
    data["days_until_expiry"] = food.days_until_expiry
    data["expiry_status"] = get_expiry_status(food)

    if food.owner:
        data["owner"] = {
            "id": food.owner.id,
            "nickname": food.owner.nickname,
            "avatar_color": food.owner.avatar_color,
        }
    return data

