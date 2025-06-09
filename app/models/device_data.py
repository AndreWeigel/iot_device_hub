from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.db.base import Base

class DeviceData(Base):
    """
    Represents a single telemetry data point reported by a device.

    Contains sensor type, value, and timestamp. Each record is associated
    with a specific IoT device.
    """
    __tablename__ = "device_data"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id",ondelete="CASCADE"), nullable=False)
    sensor_type = Column(String, nullable=False) # metric, unit
    value = Column(Float, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    device = relationship("Device", back_populates="data_points")
