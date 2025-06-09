from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession


from app.db.deps import get_db
from app.auth.auth_device_bearer import get_current_device
from app.models.device import Device
from app.models.device_data import DeviceData
from app.schemas.device_data import DeviceDataIn, DeviceDataOut
from app.schemas.device import DeviceRead

router = APIRouter()

#TODO Create endpoints for Last X data points per device
#TODO Create endpoints for Range queries: ?start=...&end=...

@router.post("/devices/data", response_model=DeviceDataOut, tags=["data_ingestion"])
async def ingest_device_data(data: DeviceDataIn,
                             device: DeviceRead = Depends(get_current_device),
                             db: AsyncSession = Depends(get_db)):
    """Ingest telemetry data from a device associated with the current authenticated user."""
    # Check if the device belongs to this user

    # Safely extract and validate device ID
    if device.id is None:
        raise HTTPException(status_code=401, detail="Invalid token: device ID is missing")

    device_id = int(device.id)
    device = await db.get(Device, device_id)
    if not device:
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
