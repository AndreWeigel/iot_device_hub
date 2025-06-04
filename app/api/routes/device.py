from fastapi import APIRouter, Depends, status, Form, HTTPException, Response
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceRead, DeviceReadWithKey, Token
from app.schemas.user import UserBase
from app.services.device_service import DeviceService
from app.auth.auth_device_handler import authenticate_device, create_device_token
from app.auth.auth_bearer import get_current_active_user
from app.db.deps import get_db

router = APIRouter()

@router.post("/device/token", response_model=Token)
async def login_device_for_access_token(device_id: int = Form(...),
                                device_key: str = Form(...),
                                 db: AsyncSession = Depends(get_db)):
    """
    Authenticates a device using device_id and device_key,
    and returns a JWT access token if valid.
    """
    device = await authenticate_device(db, device_id, device_key)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device credentials",
        )

    token = create_device_token(data={"sub": str(device.id)})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/device", response_model=List[DeviceRead])
async def get_devices_by_current_user(current_user: UserBase = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """Retrieve all devices belonging to the currently authenticated user."""
    return await DeviceService.get_devices_by_user(db, current_user.id)


@router.post("/device", response_model=DeviceReadWithKey, status_code=status.HTTP_201_CREATED)
async def register_device(new_device: DeviceCreate, current_user: UserBase = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """Register a new device for the current user."""
    return await DeviceService.create_device(db, new_device, current_user.id)


@router.put("/devices/{device_id}", response_model=DeviceRead)
async def update_device_route(device_id: int, update_data: DeviceUpdate, current_user: UserBase = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """Update a device owned by the current user."""
    return await DeviceService.update_device_for_user(db, device_id, current_user.id, update_data)

@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device_route(device_id: int, current_user: UserBase = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """Delete a device owned by the current user."""
    await DeviceService.delete_device_for_user(db, device_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)