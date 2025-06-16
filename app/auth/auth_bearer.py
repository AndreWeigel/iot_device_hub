from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.models.user import TokenData, UserInDB
from app.auth.auth_handler import SECRET_KEY, ALGORITHM
from app.services.user_service import UserService
from app.db.session import get_db_session


# OAuth2PasswordBearer defines how the token is retrieved from the request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db_session)) -> UserInDB:
    """Validates the JWT token and retrieves the current user from the database."""
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    try:
        # Decode the JWT token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        # If no subject (username) in token, raise unauthorized
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

    except JWTError:
        # Token is invalid or tampered with
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    try:
        # Retrieve the user from the database
        user = await UserService.get_user_internal(db, username)
    except HTTPException as e:
        # Convert 404 user not found to 401
        if e.status_code == 404:
            raise HTTPException(status_code=401, detail="User no longer exists")
        raise

    # Convert ORM model to Pydantic schema
    return UserInDB.model_validate(user, from_attributes=True)


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Ensures that the current user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
