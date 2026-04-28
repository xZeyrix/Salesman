from typing import Annotated
from fastapi import Depends
from backend.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from backend.models.base import Base
from backend.models.model import User, News, Message, Wallet
import logging
logger = logging.getLogger(__name__)

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
        logger.info(f"Таблицы в метадате: {Base.metadata.tables.keys()}")
        try:
            logger.info(f"Попытка синхронизации таблиц: {list(Base.metadata.tables.keys())}")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("База данных готова.")
        except Exception as e:
            logger.info(f"Запуск без пересоздания таблиц (возможно, они уже есть): {e}")

DBSessionDep = Annotated[AsyncSession, Depends(get_session)]