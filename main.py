import email
import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.schemas.user import UserInDB, UserBase, UserRead, UserUpdate, UserDelete, UserCreate, Token, TokenData
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
async def check_current_user(current_user: UserBase = Depends(get_current_active_user)):
    return current_user


@app.post("/user", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    success, _ = UserService(db).get(user, by='username')
    if success:
        raise HTTPException(status_code=400, detail="Username already registered")
    success, _ = UserService(db).get(user, by='email')
    if success:
        raise HTTPException(status_code=400, detail="Email already registered")

    success, result = UserService(db).create(user)

    if not success:
        raise HTTPException(status_code=400, detail=str(result))  # send the DB error as response

    return result

@app.put("/user", response_model=UserRead, status_code=status.HTTP_200_OK)
def update_user(new_user_data: UserUpdate, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):

    success, user = UserService(db).get(current_user.id)
    if not success or not user:
        raise HTTPException(status_code=404, detail="User not found")

    success, result = UserService(db).update(current_user.id, new_user_data)

    if not success:
        raise HTTPException(status_code=400, detail=str(result))
    return result

@app.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    success, user = UserService(db).get(current_user.id)
    if not success or not user:
        raise HTTPException(status_code=404, detail="User not found")
    success, result = UserService(db).delete(current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail=str(result))
    return

