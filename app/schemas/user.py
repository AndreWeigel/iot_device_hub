from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str or None = None


class UserBase(BaseModel):
    username: str
    email: str
    status: bool


class UserInDB(UserBase):
    hashed_password: str

