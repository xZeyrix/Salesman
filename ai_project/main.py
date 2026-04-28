from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
import logging
import sys
from backend.core.config import settings
import asyncio
from .router import router

dp = Dispatcher()

async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())