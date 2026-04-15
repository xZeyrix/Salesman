from fastapi import APIRouter

router = APIRouter(prefix='/ai', tags=['ЗАПРОСЫ К ИИ, ЧАТ И ТД'])

@router.get('/chat')
async def chat():
    pass