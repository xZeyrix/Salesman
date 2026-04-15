from typing import Annotated
from fastapi import APIRouter, Path

router = APIRouter(prefix='/stocks', tags=['ЗАПРОСЫ К БИРЖЕ, ПОЛУЧЕНИЕ ЦЕН И ТД'])

@router.get('/{name}/price')
async def chat(name: Annotated[str, Path(min_length=2, max_length=30)]):
    pass