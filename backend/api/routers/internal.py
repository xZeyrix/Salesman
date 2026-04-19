from fastapi import APIRouter, Depends, Path, Query
from typing import Annotated
from backend.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import DBSessionDep

router = APIRouter(prefix='/internal', tags=['Только для внутренних сервисов'])

@router.get('/absmemory')
async def get_absmemory(session: DBSessionDep):
    pass

@router.post('/ai-response')
async def patch_response(user_id: Annotated[int, Query()],
               session: DBSessionDep):
    pass