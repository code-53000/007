from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Box(Base):
    __tablename__ = "boxes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    floor = Column(Integer, nullable=False)
    row = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    claimer_id = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="boxes", foreign_keys=[owner_id])
    claimer = relationship("User", back_populates="claimed_boxes", foreign_keys=[claimer_id])
    foods = relationship("Food", back_populates="box", cascade="all, delete-orphan")

    @property
    def box_status(self):
        if self.is_public:
            return "active"
        if self.status == "released":
            return "released"
        if not self.expires_at:
            return "active"
        now = datetime.utcnow()
        from app.config import settings
        grace_deadline = self.expires_at + timedelta(days=settings.private_box_grace_days)
        if now > grace_deadline:
            return "released"
        if now > self.expires_at:
            return "grace"
        if now > self.expires_at - timedelta(days=1):
            return "expiring"
        return "active"
