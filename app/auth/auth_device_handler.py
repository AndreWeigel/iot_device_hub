import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets

from app.utils import now_utc


# Load environment variables from .env file
load_dotenv()

# Security settings loaded from environment
SECRET_KEY = os.getenv("API_SECRET_KEY")
ALGORITHM = os.getenv("API_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("API_ACCESS_TOKEN_EXPIRE_MINUTES", 15))


# Password hashing configuration using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_device_key():
    """Generate a new device key"""
    return secrets.token_urlsafe(32)


def verify_device_key(plain_key: str, hashed_key: str) -> bool:
    """Compares plain key to hashed key."""
    return pwd_context.verify(plain_key, hashed_key)


def hash_device_key(key: str) -> str:
    """Hashes a device key."""
    return pwd_context.hash(key)


async def authenticate_device(db, device_id: int, device_key: str):
    """Checks if a device exists and the key matches."""
    from app.services.device_service import DeviceService
    device = await DeviceService.get_device(db, device_id)

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device not found")

    if not verify_device_key(device_key, device.hashed_device_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device key")

    if not device.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Device is inactive")

    return device


def create_device_token(data: dict,  expires_delta: timedelta = timedelta(minutes=15)) -> str:
    """Generates JWT for an authenticated device."""
    to_encode = data.copy()
    expire = now_utc() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_device_token(token: str) -> dict | None:
    """Verifies JWT token and returns the payload if valid, else None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None