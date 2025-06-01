from fastapi import APIRouter, Depends, status
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceRead
from app.schemas.user import UserBase
from app.services.device_service import DeviceService
from app.auth.auth_bearer import get_current_active_user
from app.db.deps import get_db

router = APIRouter()

@router.get("/device", response_model=List[DeviceRead])
async def get_devices_by_current_user(current_user: UserBase = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """Retrieve all devices belonging to the currently authenticated user."""
    return await DeviceService.get_devices_by_user(db, current_user.id)


@router.post("/device", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
async def register_device(new_device: DeviceCreate, current_user: UserBase = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """Register a new device for the current user."""
    return await DeviceService.create_device(db, new_device, current_user.id)


@router.put("/devices/{device_id}", response_model=DeviceRead)
async def update_device_route(device_id: int, update_data: DeviceUpdate, current_user: UserBase = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """Update a device owned by the current user."""
    return await DeviceService.update_device_for_user(db, device_id, current_user.id, update_data)

@router.delete("/devices/{device_id}", response_model=DeviceRead)
async def delete_device_route(device_id: int, current_user: UserBase = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """Delete a device owned by the current user."""
    return await DeviceService.delete_device_for_user(db, device_id, current_user.id)