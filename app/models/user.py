from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr
from datetime import datetime
from app.utils import now_utc
from sqlalchemy import Column
from sqlalchemy.types import DateTime

class UserBase(SQLModel):
    """Shared base model for user data returned from or stored in the system."""
    username: str = Field(index=True)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    created_at: datetime = Field(default_factory=now_utc,
                                 sa_column=Column(DateTime(timezone=True), nullable=False))
    is_active: bool = Field(default=True)
    # Relationship: one user can have many devices
    devices: List["Device"] = Relationship(back_populates="owner")

User.model_rebuild()

class UserInDB(UserBase):
    """Internal user model representing a user record in the database."""
    id: int | None
    hashed_password: str
    is_active: bool

class UserRead(UserBase):
    """Schema for reading user details from the API."""
    username: str
    email: EmailStr
    created_at: datetime
    is_active: bool




class UserCreate(UserBase):
    """Schema for creating a new user."""
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    """Schema for updating user details."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserDelete(UserBase):
    """Schema for user deletion operations."""
    id: int


class PasswordChange(SQLModel):
    """Schema for password change request."""
    old_password: str
    new_password: str
    new_password_confirm: str


class Token(SQLModel):
    """Authentication token returned after successful login."""
    access_token: str
    token_type: str  # Typically "bearer"


class TokenData(SQLModel):
    """Data extracted from a JWT token for identity verification."""
    username: Optional[str] = None