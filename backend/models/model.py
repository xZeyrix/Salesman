from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, ForeignKey, func, Column, Integer,, Text, DateTime
from typing import Optional
from backend.models.base import Base
from enum import Enum
from sqlalchemy import 

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

class StockNews(Base):
    __tablename__ = "stock_news"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True) 
    ticker: Mapped[str] = mapped_column(String(10), index=True)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    headline: Mapped[str] = mapped_column(String(500))
    image: Mapped[Optional[str]] = mapped_column(String(500))
    related: Mapped[Optional[str]] = mapped_column(String(200))
    source: Mapped[Optional[str]] = mapped_column(String(100))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(String(500))
    datetime_unix: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())