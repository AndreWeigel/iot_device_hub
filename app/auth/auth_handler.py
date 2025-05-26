from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.schemas.user import UserInDB






SECRET_KEY = "3cee75a4a7b2089f5caef0fcd54992a4908b06b41403f3b9495dd08a7b75c066"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_db = { 'tim': {
                    'username': 'tim',
                    'email': 'tim@gmail.com',
                    'hashed_password': pwd_context.hash("somepassword"),
                    'status': True, }
}

def get_user(fake_db, username: str) -> UserInDB:
    if username in fake_db:
        user_data = fake_db[username]
        return UserInDB(**user_data)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):

    """ SUBSTITUTE THIS SHIT"""
    user = get_user(fake_db, username)
    """ Until here"""

    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
