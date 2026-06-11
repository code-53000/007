from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from app.database import Base


class CommonSeasoning(Base):
    __tablename__ = "common_seasonings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    brand = Column(String(100))
    category = Column(String(50), default="调味")
    quantity = Column(String(50))
    location_note = Column(String(200))
    added_by = Column(Integer, ForeignKey("users.id"))
    expiry_date = Column(Date)
    is_depleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    adder = relationship("User", foreign_keys=[added_by])


class SpaceNotice(Base):
    __tablename__ = "space_notices"

    id = Column(Integer, primary_key=True, index=True)
    box_id = Column(Integer, ForeignKey("boxes.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    free_up_date = Column(Date, nullable=False)
    description = Column(Text)
    space_size = Column(String(50))
    is_freed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    box = relationship("Box", foreign_keys=[box_id])
    user = relationship("User", foreign_keys=[user_id])
