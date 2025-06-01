from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DeviceDataIn(BaseModel):
    sensor_type: str = Field(..., example="temperature")
    value: float = Field(..., example=23.5)
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class DeviceDataOut(BaseModel):
    id: int
    device_id: int
    sensor_type: str
    value: float
    timestamp: datetime

    class Config:
        orm_mode = True