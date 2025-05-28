from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeviceBase(BaseModel):
    name: str
    device_type: str
    is_active: Optional[bool] = True


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    device_type: Optional[str] = None
    is_active: Optional[bool] = None
    last_seen: Optional[datetime] = None  # Optional in case you want to allow manual updates


class DeviceRead(DeviceBase):
    id: int
    user_id: int
    last_seen: datetime

