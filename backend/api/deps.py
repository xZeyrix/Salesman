from typing import Annotated

from fastapi import HTTPException, Header, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import DBSessionDep
from backend.models.model import User
from backend.models.model import Message


async def get_current_user(
    session: DBSessionDep,
    telegram_id: int | None = Header(default=None, alias="Telegram-Id"),
    ) -> User:
    
    if not telegram_id:
        raise HTTPException(status_code=401, detail="Отсутствует заголовок telegram-id")

    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(telegram_id=telegram_id, status='DEFAULT')
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]

async def last_abr_history(user: CurrentUserDep,
                           session: DBSessionDep,
                           n_abr_history: int =1) -> str | None | list[str]:
    result = await session.execute(
        select(Message.abr_history)
        .where(Message.abr_history != None, Message.user_id == user.id)
        .order_by(desc(Message.created_at))
        .limit(n_abr_history)
    )
    abr_history = result.scalars().all()
    if not abr_history:
        return None
    return abr_history[0] if n_abr_history == 1 else abr_history



ABRhistoryDep = Annotated[str | None | list[str], Depends(last_abr_history)]