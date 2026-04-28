import logging
from typing import Annotated

import httpx
from fastapi import APIRouter, Header, HTTPException, Path, Query
from sqlalchemy import desc, or_, select

from backend.api.deps import CurrentUserDep
from backend.core.database import DBSessionDep
from backend.models.model import News
from backend.schemas.news import NewsResponse
from backend.services.alpaca import alpaca

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stocks", tags=["Биржа"])

Ticker = Annotated[str, Path(min_length=1, max_length=20)]
WalletSecret = Annotated[str | None, Header(alias="X-Wallet-Secret")]

ALPACA_DATA_BASE = "https://data.alpaca.markets/v2"

@router.get("/{ticker}/price", summary="Текущая цена акции (Alpaca snapshot)")
async def get_price(ticker: Ticker):
    """
    Текущая цена через Alpaca Market Data snapshot.
    Использует серверные ключи из config (не пользовательские).
    """
    from backend.core.config import settings

    url = f"{ALPACA_DATA_BASE}/stocks/{ticker.upper()}/snapshot"
    headers = {
        "APCA-API-KEY-ID": settings.ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": settings.ALPACA_SECRET_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Тикер {ticker} не найден")
        response.raise_for_status()
        data = response.json()

        latest_trade = data.get("latestTrade", {})
        latest_quote = data.get("latestQuote", {})
        daily_bar = data.get("dailyBar", {})
        prev_daily_bar = data.get("prevDailyBar", {})

        current_price = latest_trade.get("p") or daily_bar.get("c", 0)
        prev_close = prev_daily_bar.get("c", 0)
        change = round(current_price - prev_close, 4) if prev_close else None
        change_pct = round((change / prev_close) * 100, 2) if prev_close and change else None

        return {
            "ticker": ticker.upper(),
            "current_price": current_price,
            "change": change,
            "change_percent": change_pct,
            "bid": latest_quote.get("bp"),
            "ask": latest_quote.get("ap"),
            "high": daily_bar.get("h"),
            "low": daily_bar.get("l"),
            "open": daily_bar.get("o"),
            "volume": daily_bar.get("v"),
            "prev_close": prev_close or None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка цены [{ticker}]: {e}")
        raise HTTPException(status_code=502, detail="Ошибка получения данных от Alpaca")


@router.get("/{ticker}/news", summary="Новости по тикеру (из БД)")
async def get_news(
    ticker: Ticker,
    dbsession: DBSessionDep,
    last_n: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[NewsResponse]:
    """
    ticker='all' -> последние N новостей.
    ticker='AAPL' -> новости где ticker=AAPL или AAPL в related.
    """
    try:
        if ticker.lower() == "all":
            result = await dbsession.execute(
                select(News).order_by(desc(News.datetime_unix)).limit(last_n)
            )
        else:
            t = ticker.upper()
            result = await dbsession.execute(
                select(News)
                .where(or_(News.ticker == t, News.related.contains(t)))
                .order_by(desc(News.datetime_unix))
                .limit(last_n)
            )
        return list(reversed(result.scalars().all()))

    except Exception as e:
        logger.error(f"Ошибка новостей [{ticker}]: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")

