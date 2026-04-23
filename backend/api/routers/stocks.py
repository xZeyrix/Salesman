from typing import Annotated
from fastapi import APIRouter, HTTPException, Path
from sqlalchemy import desc, or_, select
from backend.models.model import News
from backend.schemas.news import NewsResponse
from backend.core.database import DBSessionDep
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/stocks', tags=['Биржа'])
Ticker = Annotated[str, Path(min_length=2, max_length=30)]

@router.get('/{ticker}/price')
async def get_price(ticker: Ticker):
    pass

@router.get('/{ticker}/news')
async def get_news(ticker: Ticker,
                   dbsession: DBSessionDep,
                   last_n: int = 10) -> list[NewsResponse]:
    try:
        if ticker == 'all':
            result = await dbsession.execute(
            select(News).order_by(desc(News.datetime_unix)).limit(last_n)
        )
        else:
            result = await dbsession.execute(
                select(News).where(or_(
                    News.ticker == ticker, 
                    News.related.contains(ticker)
                )).order_by(desc(News.datetime_unix))
            )
        all_news = result.scalars().all()
        return list(reversed(all_news))
    except Exception as e: 
        logger.error(msg=f'Ошибка в ticker/news {e}')
        raise HTTPException(status_code=500, detail="Ошибка сервера")