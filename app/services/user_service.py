from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
from fastapi import HTTPException
from typing import Optional

from app.models.user import User, UserCreate, UserUpdate, UserRead

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """
    Service class for handling all user-related operations.

    Provides static methods for retrieving, creating, updating,
    and deleting user records from the database.
    """

    @staticmethod
    async def get_user(db: AsyncSession, identifier, by: str = "id") -> Optional[User]:
        """Retrieve a user based on a given identifier (id, email, or username)."""

        query_map = {
            "id": select(User).where(User.id == identifier),
            "email": select(User).where(User.email == identifier),
            "username": select(User).where(User.username == identifier),
        }

        query = query_map.get(by)

        result = await db.execute(query)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_internal(db: AsyncSession, username: str) -> Optional[User]:
        """Internal method to fetch a user by username.
        Raises HTTP 404 if user is not found."""

        query = select(User).where(User.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> UserRead:
        """Create a new user with unique email and username."""
        #Check if username already exists
        if await UserService.get_user(db, user_data.username, by='username'):
            raise HTTPException(status_code=400, detail="Username already registered")
        # Check if email already exists
        if await UserService.get_user(db, user_data.email, by='email'):
            raise HTTPException(status_code=400, detail="Email already registered")

        try:

            new_user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=pwd_context.hash(user_data.password)
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return UserRead.model_validate(new_user)
        except SQLAlchemyError as e:
            await db.rollback()
            print(e)
            raise HTTPException(status_code=500, detail="Failed to create user")

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, update_data: UserUpdate) -> UserRead:
        """Update user details including email, username, or password.
        Ensures no duplicate usernames or emails."""

        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        data = update_data.model_dump(exclude_unset=True)

        # Check for username conflict
        if "username" in data and data["username"] != user.username:
            query = select(User).where(User.username == data["username"], User.id != user.id)
            result = await db.execute(query)
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = data["username"]

        # Check for email conflict
        if "email" in data and data["email"] != user.email:
            query = select(User).where(User.email == data["email"], User.id != user.id)
            result = await db.execute(query)
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Email already taken")
            user.email = data["email"]

        try:
            await db.commit()
            await db.refresh(user)
            return UserRead.model_validate(user)
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update user")

    @staticmethod
    async def change_password(
            db: AsyncSession,
            user_id: int,
            old_password: str,
            new_password: str,
    ) -> None:
        user = await UserService.get_user(db, user_id, by="id")
        if not UserService.verify_password(old_password, user_id, user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        user.hashed_password = pwd_context.hash(new_password)
        await db.commit()

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> None:
        """Delete a user by ID."""

        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            await db.delete(user)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete user")

    @staticmethod
    async def verify_password(db: AsyncSession, user_id: int, plain_password: str) -> bool:
        """Verifies a plain password against a hashed password using bcrypt."""
        query = select(User.hashed_password).where(User.id == user_id)
        result = await db.execute(query)
        hashed_password = result.scalar_one_or_none()
        return pwd_context.verify(plain_password, hashed_password)
