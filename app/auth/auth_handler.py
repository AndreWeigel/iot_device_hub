import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.services.user_service import UserService

# Load environment variables from .env file
load_dotenv()

# Security settings loaded from environment
SECRET_KEY = os.getenv("API_SECRET_KEY")
ALGORITHM = os.getenv("API_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("API_ACCESS_TOKEN_EXPIRE_MINUTES", 15))


# Password hashing configuration using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 1. Hash and Verify device key
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password using bcrypt."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a password using bcrypt."""
    return pwd_context.hash(password)


# 2. Authenticate device
async def authenticate_user(db, username: str, password: str):
    """Authenticates a user by verifying their username and password."""
    try:
        user = await UserService.get_user_internal(db, username)
    except HTTPException as e:
        if e.status_code == 404:
            return None # User not found
        raise  # re-raise any other unexpected exception

    if not verify_password(password, user.hashed_password):
        return None # Password does not match

    return user


# 3. Create access token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    """Creates a JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
