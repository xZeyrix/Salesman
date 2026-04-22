from aiogram import Router, types
from ai_system.salesman import Salesman
from ai_system.type_helpers import IncMsgStructure

router = Router()
ai = Salesman()

@router.message()
async def start(message: types.Message) -> None:
    response = ai.handle(1)
    if response.status == "OK":
        await message.answer(str(response.content))
    else:
        await message.answer(response.status)