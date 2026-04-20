from typing import Annotated
from fastapi import APIRouter, Path

router = APIRouter(prefix='/stocks', tags=['Биржа'])


@router.get('/{ticker}/price')
async def get_price(ticker: Annotated[str, Path(min_length=2, max_length=30)]):
    pass