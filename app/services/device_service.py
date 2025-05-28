from fastapi import HTTPException

from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceRead

class DeviceService:
    @staticmethod
    def get_device(db: Session, device_id: int) -> DeviceRead | None:
        device = db.query(Device).filter(Device.id == device_id).first()
        return DeviceRead.model_validate(device, from_attributes=True) if device else None

    @staticmethod
    def get_devices_by_user(db: Session, user_id: int) -> list[DeviceRead]:
        devices = db.query(Device).filter(Device.user_id == user_id).all()
        return [DeviceRead.model_validate(device, from_attributes=True) for device in devices]

    @staticmethod
    def get_user_device(db: Session, device_id: int, user_id: int) -> Device:
        device = db.query(Device).filter(Device.id == device_id, Device.user_id == user_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return device

    @staticmethod
    def create_device(db: Session, device_data: DeviceCreate, user_id: int) -> DeviceRead:

        devices = DeviceService.get_devices_by_user(db, user_id)
        if any(device.name == device_data.name for device in devices):
            raise HTTPException(status_code=400, detail="Device name already exists for this user")

        device = Device(
            name=device_data.name,
            device_type=device_data.device_type,
            user_id=user_id,
            is_active=device_data.is_active if device_data.is_active is not None else True,
            last_seen=datetime.now(timezone.utc),
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        return DeviceRead.model_validate(device, from_attributes=True)

    @staticmethod
    def update_device(db: Session, device: Device, update_data: DeviceUpdate) -> DeviceRead:
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(device, field, value)
        db.commit()
        db.refresh(device)
        return DeviceRead.model_validate(device, from_attributes=True)

    @staticmethod
    def update_device_for_user(db: Session, device_id: int, user_id: int, update_data: DeviceUpdate) -> DeviceRead:
        device = DeviceService.get_user_device(db, device_id, user_id)
        return DeviceService.update_device(db, device, update_data)

    @staticmethod
    def delete_device(db: Session, device: Device) -> None:
        db.delete(device)
        db.commit()

    @staticmethod
    def delete_device_for_user(db: Session, device_id: int, user_id: int) -> None:
        device = DeviceService.get_user_device(db, device_id, user_id)
        DeviceService.delete_device(db, device)