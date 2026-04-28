from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class Wallet_SRC(Enum, str):
    ALPACA = 'ALPACA'
    TRADERNET = 'TRADERNET'

class WalletCreate(BaseModel):
    wallet_SRC: Wallet_SRC
    wallet_key: str =  Field(max_lenght=150, min_lenght=2)
    wallet_secret: str =  Field(max_lenght=150, min_lenght=2)

class WalletUpdate(BaseModel):
    wallet_SRC: Optional[Wallet_SRC]
    wallet_key: Optional[str] =  Field(default=None, max_lenght=150, min_lenght=2)
    wallet_secret: Optional[str] =  Field(default=None, max_lenght=150, min_lenght=2)

class WalletRead(BaseModel):
    wallet_SRC: Wallet_SRC
    wallet_key: str =  Field(max_lenght=150, min_lenght=2)
    wallet_secret: str =  Field(max_lenght=150, min_lenght=2)
