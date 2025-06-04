from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from app.db.base import Base

class Device(Base):
    """
    Represents an IoT device registered by a user.

    Each device is linked to a specific user and can report telemetry data.
    The device has identifying attributes and tracks its last communication timestamp.
    """
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    hashed_device_key = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_seen = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationship to user
    owner = relationship("User", back_populates="devices")
    # Relationship to device_data
    data_points = relationship("DeviceData", back_populates="device",cascade="all, delete-orphan",
    passive_deletes=True)

    def __repr__(self) -> str:
        return f"<Device (id ={self.id}, name ={self.name}, owner ={self.owner}, last_seen ={self.last_seen}, is_active ={self.is_active})> )>"
