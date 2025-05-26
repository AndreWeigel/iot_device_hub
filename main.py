import email
import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.ifc import PasswordHash
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.schemas.user import UserInDB, UserBase, Token, TokenData
from app.auth.auth_handler import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth.auth_handler import fake_db
from app.auth.auth_bearer import get_current_active_user


app = FastAPI()

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user( form_data.username, form_data.password)
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


