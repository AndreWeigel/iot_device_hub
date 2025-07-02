from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from app.utils import now_utc
from sqlalchemy import Column
from sqlalchemy.types import DateTime





class DeviceDataIn(SQLModel):
    """Schema for incoming telemetry data from a device."""

    reading_type: str
    value: float
    timestamp: Optional[datetime] = Field(
        default_factory=now_utc,
        description="Timestamp of the data point. Defaults to current UTC time."
    )


class DeviceDataOut(DeviceDataIn):
    """Schema for telemetry data returned from the API."""
    id: int
    device_id: int


class DeviceData(SQLModel, table=True):
    """
    Represents a single telemetry data point reported by a device.

    Contains sensor type, value, and timestamp. Each record is associated
    with a specific IoT device.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: int = Field(foreign_key="device.id")
    reading_type: str
    value: float
    timestamp: datetime = Field(default_factory=now_utc,
                                 sa_column=Column(DateTime(timezone=True), nullable=False))

    device: Optional["Device"] = Relationship(back_populates="data_points")
