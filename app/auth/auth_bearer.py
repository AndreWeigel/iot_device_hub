from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.schemas.user import TokenData, UserInDB
from app.auth.auth_handler import SECRET_KEY, ALGORITHM
from app.services.user_service import UserService
from app.db.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    try:
        user = await UserService.get_user_internal(db, username)
    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(status_code=401, detail="User no longer exists")
        raise

    return UserInDB.model_validate(user, from_attributes=True)

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
