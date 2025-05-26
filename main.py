import email
import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.ifc import PasswordHash
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.schemas.user import UserInDB, UserBase, UserRead, UserCreate, Token, TokenData
from app.services.user_service import UserService
from app.auth.auth_handler import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth.auth_bearer import get_current_active_user
from app.db.deps import get_db
from sqlalchemy.orm import Session

app = FastAPI()

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"},)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}
                                       , expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
@app.get("/user", response_model=UserBase)
async def get_current_user_yes(current_user: UserBase = Depends(get_current_active_user)):
    return current_user


@app.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # if get_user_by_username(db, user.username):
    #     raise HTTPException(status_code=400, detail="Username already registered")
    # if get_user_by_email(db, user.email):
    #     raise HTTPException(status_code=400, detail="Email already registered")

    success, result = UserService(db).create(user)

    if not success:
        raise HTTPException(status_code=400, detail=str(result))  # send the DB error as response

    return result



