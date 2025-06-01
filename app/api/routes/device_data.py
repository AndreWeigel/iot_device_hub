from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.auth.auth_bearer import get_current_active_user
from app.models.device import Device
from app.models.device_data import DeviceData
from app.schemas.device_data import DeviceDataIn, DeviceDataOut
from app.schemas.user import UserBase

router = APIRouter()


@router.post("/devices/{device_id}/data", response_model=DeviceDataOut)
async def ingest_device_data(device_id: int, data: DeviceDataIn, db: AsyncSession = Depends(get_db),
                            current_user: UserBase = Depends(get_current_active_user)):
    """Ingest telemetry data from a device associated with the current authenticated user."""
    # Check if the device belongs to this user
    device = await db.get(Device, device_id)
    if not device or device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="This device is not authorized")

    # Store the telemetry data
    db_data = DeviceData(
        device_id=device_id,
        sensor_type=data.sensor_type,
        value=data.value,
        timestamp=data.timestamp,
    )

    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)

    return db_data
