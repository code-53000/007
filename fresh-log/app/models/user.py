from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    nickname = Column(String(50), nullable=False)
    avatar_color = Column(String(20), default="#1989fa")
    hashed_password = Column(String(255), nullable=False)
    room_number = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    boxes = relationship("Box", back_populates="owner", foreign_keys="Box.owner_id")
    foods = relationship("Food", back_populates="owner", foreign_keys="Food.owner_id")
    cleanup_records = relationship("CleanupRecord", back_populates="operator")
    operation_logs = relationship("OperationLog", back_populates="user")

    claimed_boxes = relationship(
        "Box",
        back_populates="claimer",
        foreign_keys="Box.claimer_id",
    )
