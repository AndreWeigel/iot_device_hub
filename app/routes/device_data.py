from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime


from app.db.session import get_db_session
from app.auth.auth_device_bearer import get_current_device
from app.auth.auth_bearer import get_current_user
from app.models.device import Device, DeviceRead
from app.models.device_data import DeviceData, DeviceDataIn, DeviceDataOut


router = APIRouter()



@router.post("/devices/data", response_model=DeviceDataOut, tags=["data_ingestion"])
async def ingest_device_data(data: DeviceDataIn,
                             device: DeviceRead = Depends(get_current_device),
                             db: AsyncSession = Depends(get_db_session)):
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
        reading_type=data.reading_type,
        value=data.value,
        timestamp=data.timestamp,
    )

    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)

    return db_data




@router.get("/devices/{device_id}/data/last", response_model=list[DeviceDataOut], tags=["device_data"])
async def get_last_device_data(
    device_id: int = Path(..., description="ID of the device"),
    limit: int = Query(10, gt=0, description="Number of recent data points to return"),
    db: AsyncSession = Depends(get_db_session),
    user = Depends(get_current_user),  # Use get_current_admin if needed
):
    """Get the last X data points for the given device (admin/user scoped)."""

    # Optional: Add ownership check (if user is not admin)
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Add device-user ownership validation here if needed

    result = await db.execute(
        select(DeviceData)
        .where(DeviceData.device_id == device_id)
        .order_by(DeviceData.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/devices/{device_id}/data/range", response_model=list[DeviceDataOut], tags=["device_data"])
async def get_device_data_in_range(
    device_id: int = Path(..., description="ID of the device"),
    start: str = Query(..., description="Start datetime in ISO 8601 format (e.g., 2025-07-24T00:00:00 or 2025-07-24T00:00:00Z)"),
    end: str = Query(..., description="End datetime in ISO 8601 format (e.g., 2025-07-25T00:00:00 or 2025-07-25T00:00:00Z)"),
    db: AsyncSession = Depends(get_db_session),
    user = Depends(get_current_user),  # Or get_current_admin
):
    """Get data points between start and end timestamps for a given device."""

    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO 8601.")

    if start_dt >= end_dt:
        raise HTTPException(status_code=400, detail="Start must be before end.")

    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Optional: Add access control check for user ownership

    result = await db.execute(
        select(DeviceData)
        .where(
            DeviceData.device_id == device_id,
            DeviceData.timestamp >= start_dt,
            DeviceData.timestamp <= end_dt,
        )
        .order_by(DeviceData.timestamp.asc())
    )
    return result.scalars().all()


