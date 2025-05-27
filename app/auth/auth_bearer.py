from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.schemas.user import TokenData, UserInDB
from app.auth.auth_handler import SECRET_KEY, ALGORITHM
from app.services.user_service import UserService
from sqlalchemy.orm import Session
from app.db.deps import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
        raise credentials_exception

    success, result = UserService(db).get(username, by='username')
    if result is None:
        raise credentials_exception
    return result

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if not current_user.status:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
