from typing import Annotated

from fastapi import APIRouter, Path, Query
from backend.api.deps import CurrentUserDep
from backend.core.database import DBSessionDep
router = APIRouter(prefix='/ai', tags=['ИИ и чат'])

@router.get('/chat/history')
async def get_chat_history(last_n_messages: Annotated[int, Query(ge=0)],
                           user: CurrentUserDep,
                           dbsession: DBSessionDep):
    pass

@router.get('/analysis/{ticker}')
async def analysis(ticker: Annotated[str, Path(min_length=2, max_length=30)],
                   user: CurrentUserDep):
    pass