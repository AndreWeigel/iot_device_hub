from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    """
    Represents a user in the IoT Hub system.

    Users can own multiple IoT devices. Each user has authentication details
    and a status flag indicating whether the account is active.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default = True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    devices = relationship("Device", back_populates="owner")

    def __repr__(self) -> str:
        return f"User (id ={self.id}, username ={self.username}, is_active ={self.is_active})> "
