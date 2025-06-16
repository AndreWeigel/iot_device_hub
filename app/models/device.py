from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from app.models.user import User
from datetime import datetime
from app.utils import now_utc
from sqlalchemy.types import DateTime
from sqlalchemy import Column


class DeviceBase(SQLModel):
    """Shared base model for device data."""
    name: str
    device_type: str
    is_active: Optional[bool] = Field(default=True)


class Device(DeviceBase, table=True):
    """
    Represents an IoT device registered by a user.

    Each device is linked to a specific user and can report telemetry data.
    The device has identifying attributes and tracks its last communication timestamp.
    """
    id: int | None = Field(default=None, primary_key=True)

    hashed_device_key: str
    created_at: datetime = Field(default_factory=now_utc,
                                 sa_column=Column(DateTime(timezone=True), nullable=False)) # force timezone aawareness
    last_seen: Optional[datetime] = Field(default_factory=now_utc,
                                          sa_column=Column(DateTime(timezone=True), nullable=False))

    user_id: int = Field(foreign_key="user.id")

    owner: Optional[User] = Relationship(back_populates="devices")

    # Relationship to device_data
    data_points: List["DeviceData"] = Relationship(
        back_populates="device",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        }
    )

class DeviceCreate(DeviceBase):
    """Schema for creating a new IoT device."""
    pass

class DeviceRead(DeviceBase):
    """Schema for reading device data from the API."""
    id: int
    user_id: int
    last_seen: datetime

class DeviceReadWithKey(DeviceRead):
    """
    Schema for reading device data and device key from the API.
    Gets returned after creating a new IoT device. ONLY!
    """
    device_key: str


class DeviceReadWithHashedKey(DeviceRead):
    """Schema for reading device data and hashed device key from the API."""
    hashed_device_key: str


class DeviceUpdate(DeviceBase):
    """Schema for updating an existing IoT device."""
    name: Optional[str] = None
    device_type: Optional[str] = None
    is_active: Optional[bool] = None
    last_seen: Optional[datetime] = None

class DeviceDelete(SQLModel):
    """Schema for deleting an existing IoT device."""
    id: int | None


class Token(SQLModel):
    """
    Authentication token returned after successful login.
    """
    access_token: str
    token_type: str  # Typically "bearer"
