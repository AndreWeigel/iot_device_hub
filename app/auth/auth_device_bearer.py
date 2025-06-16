# auth_device_bearer.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.auth.auth_device_handler import SECRET_KEY, ALGORITHM
from app.models.device import DeviceRead
from app.services.device_service import DeviceService


async def get_current_device(request: Request,
                             db: AsyncSession = Depends(get_db_session)) -> DeviceRead:
    """Validates the JWT token and returns the current device."""

    credentials_exception = HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate device credentials",
                    headers={"WWW-Authenticate": "Bearer"},
    )

    # Extract token from header
    auth: str = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(auth)

    if not auth or scheme.lower() != "bearer" or not token:
        raise credentials_exception

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        # Decode the JWT and extract the subject (device_id)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        device_id = payload.get("sub")

        if device_id is None:
            raise credentials_exception

        try:
            device_id = int(device_id)
        except ValueError:
            raise credentials_exception


    except JWTError:
        raise credentials_exception

    # Fetch device from DB
    device = await DeviceService.get_device(db, device_id)
    if device is None or not device.is_active:
        raise credentials_exception

    # Return validated Pydantic model
    return DeviceRead.model_validate(device, from_attributes=True)
