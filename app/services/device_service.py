from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceRead


class DeviceService:
    """
    Service class for handling operations related to IoT devices.

    Includes methods to create, retrieve, update, and delete devices,
    ensuring users can only access and manage their own devices.
    """

    @staticmethod
    async def get_device(db: AsyncSession, device_id: int) -> DeviceRead | None:
        """Retrieve a device by its ID."""
        query = select(Device).where(Device.id == device_id)
        result = await db.execute(query)
        device = result.scalar_one_or_none()
        return DeviceRead.model_validate(device, from_attributes=True) if device else None

    @staticmethod
    async def get_devices_by_user(db: AsyncSession, user_id: int) -> list[DeviceRead]:
        """Retrieve all devices owned by a specific user."""
        query = select(Device).where(Device.user_id == user_id)
        result = await db.execute(query)
        devices = result.scalars().all()
        return [DeviceRead.model_validate(device, from_attributes=True) for device in devices]

    @staticmethod
    async def get_user_device(db: AsyncSession, device_id: int, user_id: int) -> Device:
        """Retrieve a device by its ID, ensuring it belongs to the specified user."""
        query = select(Device).where(Device.id == device_id, Device.user_id == user_id)
        result = await db.execute(query)
        device = result.scalar_one_or_none()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return device

    @staticmethod
    async def create_device(db: AsyncSession, device_data: DeviceCreate, user_id: int) -> DeviceRead:
        """Create a new device for a given user, ensuring the name is unique per user."""
        # Enforce sure unique device name for user
        query = select(Device).where(
            Device.user_id == user_id,
            Device.name == device_data.name
        )
        result = await db.execute(query)
        existing_device = result.scalar_one_or_none()
        if existing_device:
            raise HTTPException(status_code=400, detail="Device name already exists for this user")

        device = Device(
            name=device_data.name,
            device_type=device_data.device_type,
            user_id=user_id,
            is_active=device_data.is_active if device_data.is_active is not None else True,
            last_seen=datetime.now(timezone.utc),
        )
        db.add(device)
        await db.commit()
        await db.refresh(device)
        return DeviceRead.model_validate(device, from_attributes=True)

    @staticmethod
    async def update_device(db: AsyncSession, device: Device, update_data: DeviceUpdate) -> DeviceRead:
        """Update an existing device with new data."""
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(device, field, value)
        await db.commit()
        await db.refresh(device)
        return DeviceRead.model_validate(device, from_attributes=True)

    @staticmethod
    async def update_device_for_user(db: AsyncSession, device_id: int, user_id: int, update_data: DeviceUpdate) -> DeviceRead:
        """Update a device that belongs to a specific user."""
        device = await DeviceService.get_user_device(db, device_id, user_id)
        return await DeviceService.update_device(db, device, update_data)

    @staticmethod
    async def delete_device(db: AsyncSession, device: Device) -> None:
        """Permanently delete a device."""
        await db.delete(device)
        await db.commit()

    @staticmethod
    async def delete_device_for_user(db: AsyncSession, device_id: int, user_id: int) -> None:
        """Delete a device that belongs to a specific user."""
        device = await DeviceService.get_user_device(db, device_id, user_id)
        await DeviceService.delete_device(db, device)