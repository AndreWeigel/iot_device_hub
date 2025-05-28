from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from datetime import datetime, timezone

from app.db.base import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default = True, nullable=False)
    created_at = Column(DateTime, default = datetime.now(timezone.utc), nullable=False)

    devices = relationship("Device", back_populates="owner")
