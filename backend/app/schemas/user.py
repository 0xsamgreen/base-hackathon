from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    wallet_address: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None
    kyc: Optional[bool] = None
    wallet_address: Optional[str] = None
    private_key: Optional[str] = None


class User(UserBase):
    id: int
    kyc: bool
    private_key: Optional[str] = None

    class Config:
        orm_mode = True


class UserInDB(User):
    pass
