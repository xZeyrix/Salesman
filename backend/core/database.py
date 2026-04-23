from typing import Annotated
from fastapi import Depends
from backend.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from backend.models.base import Base
from backend.models.model import User, News, Message


engine = create_async_engine(str(settings.DB_URL),
                             connect_args={"ssl": True})

new_session = async_sessionmaker(engine, 
                                expire_on_commit=False,
                                class_=AsyncSession)

async def get_session():
    async with new_session() as session:
        yield session

async def db_begin():
    async with engine.begin() as conn:
        print(f"Таблицы в метадате: {Base.metadata.tables.keys()}")
        await conn.run_sync(Base.metadata.create_all)

DBSessionDep = Annotated[AsyncSession, Depends(get_session)]