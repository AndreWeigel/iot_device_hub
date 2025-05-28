from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.services.user_service import UserService
from fastapi import HTTPException

from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def authenticate_user(db, username: str, password: str):
    try:
        user = UserService.get_user_internal(db, username)
    except HTTPException as e:
        if e.status_code == 404:
            return None
        raise  # re-raise any other unexpected exception

    if not verify_password(password, user.hashed_password):
        return None

    return user

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
