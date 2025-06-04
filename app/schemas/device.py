from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeviceBase(BaseModel):
    """
    Shared base model for device data.

    Contains common fields used in both input and output operations.
    """
    name: str
    device_type: str
    is_active: Optional[bool] = True


class DeviceCreate(DeviceBase):
    """
    Schema for creating a new IoT device.

    Inherits all required fields from DeviceBase.
    """
    pass


class DeviceUpdate(BaseModel):
    """
    Schema for updating an existing IoT device.

    Supports partial updates. The `last_seen` field can be set manually if needed.
    """
    name: Optional[str] = None
    device_type: Optional[str] = None
    is_active: Optional[bool] = None
    last_seen: Optional[datetime] = None


class DeviceRead(DeviceBase):
    """
    Schema for reading device data from the API.

    Includes device ID, user ID, and last seen timestamp.
    """
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
    """
    Schema for reading device data and device key from the API.
    Gets returned after creating a new IoT device. ONLY!
    """
    hashed_device_key: str

class Token(BaseModel):
    """
    Authentication token returned after successful login.
    """
    access_token: str
    token_type: str  # Typically "bearer"
