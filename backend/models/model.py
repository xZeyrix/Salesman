from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Boolean, String, ForeignKey, func, Text, DateTime
from typing import Optional
from backend.models.base import Base
from cryptography.fernet import Fernet
from sqlalchemy.dialects.postgresql import ARRAY
from backend.core.config import settings

cipher_suite = Fernet(settings.FERNET_KEY.encode())


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)

    wallet: Mapped["Wallet"] = relationship(back_populates="user", uselist=False)


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

    # Единственная колонка для секрета — хранит зашифрованное значение.
    # Называем атрибут с подчёркиванием, колонка в БД — wallet_secret.
    _wallet_secret: Mapped[str] = mapped_column("wallet_secret", String(512))

    user: Mapped["User"] = relationship(back_populates="wallet")

    @property
    def wallet_secret(self) -> str:
        return cipher_suite.decrypt(self._wallet_secret.encode()).decode()

    @wallet_secret.setter
    def wallet_secret(self, value: str) -> None:
        self._wallet_secret = cipher_suite.encrypt(value.encode()).decode()


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    alpaca_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    ticker: Mapped[Optional[str]] = mapped_column(String(10), index=True)
    related_symbols: Mapped[list[str]] = mapped_column(ARRAY(String), server_default="{}")

    category: Mapped[Optional[str]] = mapped_column(String(50))
    headline: Mapped[str] = mapped_column(String(1000))
    summary: Mapped[Optional[str]] = mapped_column(Text)

    source: Mapped[Optional[str]] = mapped_column(String(100))
    url: Mapped[Optional[str]] = mapped_column(Text)
    image: Mapped[Optional[str]] = mapped_column(Text)

    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())