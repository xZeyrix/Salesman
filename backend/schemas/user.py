from pydantic import BaseModel
from typing import Optional
from enum import Enum

class UserStatus(str, Enum):
    DEFAULT = 'DEFAULT'
    PREMIUM = 'PREMIUM'
    DEVELOPER = 'DEVELOPER'

class UserCreate(BaseModel):
    telegram_id: int
    status: UserStatus | None = UserStatus.DEFAULT
    

class UserUpdate(BaseModel):
    pass