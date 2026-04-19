from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    telegram_id: int
    wallet_key: Optional[str]

class UserUpdate(BaseModel):
    wallet_key: Optional[str]