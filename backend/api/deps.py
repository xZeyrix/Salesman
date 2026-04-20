from typing import Annotated

from fastapi import HTTPException, Header, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_session
from backend.models.model import User


async def get_current_user(
    telegram_id: int | None = Header(default=None, alias="Telegram-Id"),
    session: AsyncSession = Depends(get_session),
    ) -> User:
    
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Отсутствует заголовок telegram-id")

    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Авторегистрация нового пользователя"
        user = User(telegram_id=telegram_id)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]