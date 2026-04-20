from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String
from typing import Optional
from backend.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    wallet_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
