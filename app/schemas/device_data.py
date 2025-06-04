from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class DeviceDataIn(BaseModel):
    """
    Schema for incoming telemetry data from a device.

    Includes sensor type, value, and an optional timestamp.
    If no timestamp is provided, the current UTC time is used.
    """

    sensor_type: str
    value: float
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the data point. Defaults to current UTC time."
    )


class DeviceDataOut(BaseModel):
    """
    Schema for telemetry data returned from the API.

    Includes the data ID, device ID, and all associated sensor details.
    """
    id: int
    device_id: int
    sensor_type: str
    value: float
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
