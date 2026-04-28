import logging
from typing import Annotated
from fastapi import APIRouter, Body, HTTPException, Path, Query
from ai_project.ai_system.type_helpers import IncMsgStructure
from backend.api.deps import CurrentUserDep,  ABRhistoryDep
from backend.core.database import DBSessionDep
from backend.schemas.chat import MessageRequest, MessageResponse, Role, Mode
from backend.models.model import Message
from sqlalchemy import desc, select
from ai_project.ai_system.salesman import Salesman
logger = logging.getLogger(__name__)

router = APIRouter(prefix='/ai', tags=['ИИ и чат'])
ai = Salesman()

@router.get('/chat/history', response_model=list[MessageResponse], description='сообщении от старых к новым')
async def get_chat_history(user: CurrentUserDep,
                           dbsession: DBSessionDep,
                           last_n_messages: Annotated[int, Query(ge=0, le=100)] = 100) -> list[MessageResponse]:
    try:
        result = await dbsession.execute(
            select(Message).where(Message.user_id == user.id).order_by(desc(Message.created_at)).limit(last_n_messages)
        )
        chat_messages = result.scalars().all()
        return list(reversed(chat_messages))
    except Exception as e:
        logger.error(msg=f'Ошибка в chat/history {e}')
        raise HTTPException(status_code=500, detail="Ошибка сервера")

@router.post('/sendmessage', response_model=MessageResponse)
async def send_message(user: CurrentUserDep,
                       message: Annotated[MessageRequest, Body()],
                       abr_history: ABRhistoryDep,
                       dbsession: DBSessionDep) -> MessageResponse:
    try:
        user_msg = Message(
                user_id = user.id,
                role = Role.USER,
                mode = Mode.DEFAULT,
                abr_history = None,
                text = message.text,
        )
        airesponse = await ai.handle(IncMsgStructure(user_id=user.telegram_id,
                                                     history=abr_history, 
                                                     text=message.text,
                                                     content_type="text"))
        if not airesponse.status == "OK":
            dbsession.add(user_msg)
            await dbsession.commit()
            raise HTTPException(status_code=502, detail=f"Ошибка от ИИ {airesponse.status}")
        user_msg.replied = True
        dbsession.add(user_msg)
        ai_msg = Message(
            user_id = user.id,
            role = Role.AI,
            mode = Mode.DEFAULT,
            abr_history = airesponse.content.history,
            text= airesponse.content.response 
        )
        dbsession.add(ai_msg)
        await dbsession.commit()
        await dbsession.refresh(ai_msg) 
        return ai_msg
    except HTTPException:
        raise
    except Exception as e:
        await dbsession.rollback()
        logger.error(msg=f'Ошибка в sendmessage {e}')
        raise HTTPException(status_code=500, detail="Ошибка сервера")