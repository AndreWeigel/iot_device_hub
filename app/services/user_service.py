from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserRead
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @staticmethod
    def get_user(db: Session, identifier, by: str = "id") -> UserRead:
        query = {
            "id": lambda val: db.query(User).get(val),
            "email": lambda val: db.query(User).filter(User.email == val).first(),
            "username": lambda val: db.query(User).filter(User.username == val).first(),
        }

        user = query.get(by, lambda _: None)(identifier)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserRead.model_validate(user)

    @staticmethod
    def get_user_internal(db: Session, username: str) -> User:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> UserRead:
        try:
            new_user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=pwd_context.hash(user_data.password)
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return UserRead.model_validate(new_user)
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create user")

    @staticmethod
    def update_user(db: Session, user_id: int, update_data: UserUpdate) -> UserRead:
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        data = update_data.dict(exclude_unset=True)

        # Check for username conflict
        if "username" in data and data["username"] != user.username:
            if db.query(User).filter(User.username == data["username"], User.id != user.id).first():
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = data["username"]

        # Check for email conflict
        if "email" in data and data["email"] != user.email:
            if db.query(User).filter(User.email == data["email"], User.id != user.id).first():
                raise HTTPException(status_code=400, detail="Email already taken")
            user.email = data["email"]

        # Update password
        if "password" in data:
            user.hashed_password = pwd_context.hash(data["password"])

        try:
            db.commit()
            db.refresh(user)
            return UserRead.model_validate(user)
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update user")

    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            db.delete(user)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete user")
