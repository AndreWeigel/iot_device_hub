from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """
    Shared base model for user data returned from or stored in the system.
    """
    username: str
    email: str
    is_active: bool


class UserInDB(UserBase):
    """
    Internal user model representing a user record in the database.

    Includes hashed password and ID, and enables loading from ORM objects.
    """
    id: int
    hashed_password: str
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Used in registration or admin creation flows.
    """
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    """
    Schema for reading user details from the API.

    Excludes sensitive fields like password.
    """
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """
    Schema for updating user details.

    Supports partial updates. Password will be hashed if provided.
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserDelete(BaseModel):
    """
    Schema for user deletion operations.

    May contain identifying info like username for soft-deletion or audit.
    """
    username: Optional[str] = None


class Token(BaseModel):
    """
    Authentication token returned after successful login.
    """
    access_token: str
    token_type: str  # Typically "bearer"


class TokenData(BaseModel):
    """
    Data extracted from a JWT token for identity verification.
    """
    username: Optional[str] = None
