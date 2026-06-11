from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.database import Base


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(50), default="其他")
    quantity = Column(Float, default=1.0)
    unit = Column(String(20), default="份")
    box_id = Column(Integer, ForeignKey("boxes.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stored_at = Column(DateTime, default=datetime.utcnow)
    expiry_days = Column(Integer, nullable=False)
    notes = Column(Text)
    is_cleaned = Column(Boolean, default=False)
    cleaned_at = Column(DateTime)
    cleaned_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    box = relationship("Box", back_populates="foods")
    owner = relationship("User", back_populates="foods", foreign_keys=[owner_id])

    @property
    def expiry_date(self) -> datetime:
        return self.stored_at + timedelta(days=self.expiry_days)

    @property
    def is_expired(self) -> bool:
        if self.is_cleaned:
            return False
        return datetime.utcnow() > self.expiry_date

    @property
    def days_until_expiry(self) -> int:
        if self.is_cleaned:
            return 999
        delta = self.expiry_date - datetime.utcnow()
        return delta.days
