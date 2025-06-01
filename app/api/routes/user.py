from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

# Pydantic schemas
from app.schemas.user import (
    UserInDB,
    UserBase,
    UserRead,
    UserUpdate,
    UserDelete,
    UserCreate,
    Token
)

# Business logic and authentication
from app.services.user_service import UserService
from app.auth.auth_handler import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth.auth_bearer import get_current_active_user
from app.db.deps import get_db

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Authenticates a user and returns a JWT access token.

    Accepts form data with username and password. If credentials are valid,
    generates and returns a bearer token for use in subsequent authenticated requests.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/user", response_model=UserBase)
async def check_current_user(current_user: UserBase = Depends(get_current_active_user)):
    """
    Returns the currently authenticated user.

    Used for session checks or frontend auto-login verification.
    """
    return current_user

@router.post("/user", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user account.

    Returns full user profile on success.
    """
    return await UserService.create_user(db, user)

@router.put("/user", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user(new_user_data: UserUpdate, db: AsyncSession = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    """
    Updates the current user's account details.

    Only accessible to authenticated users.
    """
    return await UserService.update_user(db, current_user.id, new_user_data)

@router.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: AsyncSession = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    """
    Deletes the authenticated user's account.

    Returns 204 No Content on success.
    """
    await UserService.delete_user(db, current_user.id)
