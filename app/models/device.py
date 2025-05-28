from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to user
    owner = relationship("User", back_populates="devices")

    def __repr__(self) -> str:
        return f"<Device (id ={self.id}, name ={self.name}, owner ={self.owner}, last_seen ={self.last_seen}, is_active ={self.is_active})> )>"
