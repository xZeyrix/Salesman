from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Boolean, String, ForeignKey, func, Column, Integer, Text, DateTime, Enum
from typing import Optional
from backend.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    wallet_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    mode: Mapped[str] = mapped_column(String(30), server_default="default")
    text: Mapped[str] = mapped_column(String(1000))
    abr_history: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    replied: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
class Wallet(Base):
    __tablename__ = "wallets"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    wallet_src: Mapped[str] = mapped_column(String(20))
    wallet_key: Mapped[str] = mapped_column(String(255))
    wallet_secret: Mapped[str] = mapped_column(String(255))
    _wallet_secret: Mapped[str] = mapped_column("wallet_secret", String(255))
    @property
    def wallet_secret(self) -> str:
        decrypted_text = cipher_suite.decrypt(self._wallet_secret.encode())
        return decrypted_text.decode()
    @wallet_secret.setter
    def wallet_secret(self, value: str):
        encrypted_text = cipher_suite.encrypt(value.encode())
        self._wallet_secret = encrypted_text.decode()
    
class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True) 
    finhub_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    ticker: Mapped[str] = mapped_column(String(10), index=True, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    headline: Mapped[str] = mapped_column(String(500))
    image: Mapped[Optional[str]] = mapped_column(String(500))
    related: Mapped[Optional[str]] = mapped_column(String(200))
    source: Mapped[Optional[str]] = mapped_column(String(100))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(String(500))
    datetime_unix: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
