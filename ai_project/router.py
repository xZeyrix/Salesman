from aiogram import Router, types
from ai_system.salesman import Salesman

router = Router()
ai = Salesman()

@router.message()
async def start(message: types.Message) -> None:
    await message.answer(ai.handle(message))