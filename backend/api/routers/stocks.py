"""
Router: /stocks — рыночные данные и кошелёк через Alpaca Markets.

Эндпоинты:
  GET  /stocks/{ticker}/price          — текущая цена (Alpaca snapshot)
  GET  /stocks/{ticker}/news           — новости из БД
  GET  /stocks/wallet/account          — баланс счёта (Alpaca)
  GET  /stocks/wallet/positions        — портфель / позиции (Alpaca)
  GET  /stocks/wallet/trades           — история сделок (Alpaca FILL activities)
  GET  /stocks/wallet/orders           — история ордеров (Alpaca)
  GET  /stocks/wallet/history          — equity curve портфеля (Alpaca)

Ключи Alpaca (пользовательские):
  api_key    -> User.wallet_key  (сохраняется через PATCH /user/update)
  secret_key -> заголовок X-Wallet-Secret (не хранится в БД)
"""

import logging
from typing import Annotated

import httpx
from fastapi import APIRouter, Header, HTTPException, Path, Query
from sqlalchemy import desc, or_, select

from backend.api.deps import CurrentUserDep
from backend.core.database import DBSessionDep
from backend.models.model import News
from backend.schemas.news import NewsResponse
from backend.services.alpaca import alpaca   # singleton клиент

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stocks", tags=["Биржа"])

Ticker = Annotated[str, Path(min_length=1, max_length=20)]
WalletSecret = Annotated[str | None, Header(alias="X-Wallet-Secret")]

ALPACA_DATA_BASE = "https://data.alpaca.markets/v2"


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _wallet_keys(user, secret: str | None) -> tuple[str, str]:
    if not user.wallet_key:
        raise HTTPException(
            status_code=400,
            detail="Кошелёк Alpaca не привязан. "
                   "Добавьте API-ключ через PATCH /user/update (поле wallet_key).",
        )
    if not secret:
        raise HTTPException(
            status_code=400,
            detail="Необходим заголовок X-Wallet-Secret с секретным ключом Alpaca.",
        )
    return user.wallet_key, secret


def _alpaca_error(result) -> HTTPException:
    msg = result.error.message if result.error else "неизвестная ошибка"
    code = result.error.code if result.error else 502
    status = 401 if code == 401 else 502
    return HTTPException(status_code=status, detail=f"Ошибка Alpaca: {msg}")


# ──────────────────────────────────────────────
# Рыночные данные
# ──────────────────────────────────────────────

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


# ──────────────────────────────────────────────
# Кошелёк Alpaca
# ──────────────────────────────────────────────

@router.get("/wallet/account", summary="Баланс счёта Alpaca")
async def get_wallet_account(
    user: CurrentUserDep,
    x_wallet_secret: WalletSecret = None,
):
    """
    Баланс, покупательная способность, equity, cash.
    wallet_key добавляется через PATCH /user/update.
    Секрет: заголовок X-Wallet-Secret.
    """
    api_key, secret_key = _wallet_keys(user, x_wallet_secret)
    result = await alpaca.get_account(api_key, secret_key)
    if not result.ok:
        raise _alpaca_error(result)

    acc = result.data
    return {
        "account_number": acc.get("account_number"),
        "status": acc.get("status"),
        "currency": acc.get("currency", "USD"),
        "cash": acc.get("cash"),
        "buying_power": acc.get("buying_power"),
        "portfolio_value": acc.get("portfolio_value"),
        "equity": acc.get("equity"),
        "last_equity": acc.get("last_equity"),
        "long_market_value": acc.get("long_market_value"),
        "short_market_value": acc.get("short_market_value"),
        "day_trade_count": acc.get("daytrade_count"),
        "trading_blocked": acc.get("trading_blocked"),
        "pattern_day_trader": acc.get("pattern_day_trader"),
    }


@router.get("/wallet/positions", summary="Открытые позиции / портфель (Alpaca)")
async def get_wallet_positions(
    user: CurrentUserDep,
    x_wallet_secret: WalletSecret = None,
):
    """Список текущих позиций: тикер, кол-во, цена входа, текущая цена, P&L."""
    api_key, secret_key = _wallet_keys(user, x_wallet_secret)
    result = await alpaca.get_positions(api_key, secret_key)
    if not result.ok:
        raise _alpaca_error(result)

    return [
        {
            "symbol": p.get("symbol"),
            "qty": p.get("qty"),
            "side": p.get("side"),
            "avg_entry_price": p.get("avg_entry_price"),
            "current_price": p.get("current_price"),
            "market_value": p.get("market_value"),
            "cost_basis": p.get("cost_basis"),
            "unrealized_pl": p.get("unrealized_pl"),
            "unrealized_plpc": p.get("unrealized_plpc"),
            "change_today": p.get("change_today"),
        }
        for p in result.data
    ]


@router.get("/wallet/trades", summary="История исполненных сделок (Alpaca)")
async def get_wallet_trades(
    user: CurrentUserDep,
    x_wallet_secret: WalletSecret = None,
    page_size: Annotated[int, Query(ge=1, le=200)] = 50,
    after: Annotated[str | None, Query(description="ISO: 2024-01-01T00:00:00Z")] = None,
    until: Annotated[str | None, Query(description="ISO: 2024-12-31T23:59:59Z")] = None,
):
    """Исполненные сделки (FILL activities): тикер, сторона, кол-во, цена, время."""
    api_key, secret_key = _wallet_keys(user, x_wallet_secret)
    result = await alpaca.get_activities(
        api_key, secret_key,
        activity_type="FILL",
        page_size=page_size,
        after=after,
        until=until,
    )
    if not result.ok:
        raise _alpaca_error(result)

    return [
        {
            "id": a.get("id"),
            "symbol": a.get("symbol"),
            "side": a.get("side"),
            "qty": a.get("qty"),
            "price": a.get("price"),
            "type": a.get("type"),
            "transaction_time": a.get("transaction_time"),
            "order_id": a.get("order_id"),
        }
        for a in result.data
    ]


@router.get("/wallet/orders", summary="История ордеров (Alpaca)")
async def get_wallet_orders(
    user: CurrentUserDep,
    x_wallet_secret: WalletSecret = None,
    status: Annotated[str, Query(description="open | closed | all")] = "all",
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    after: Annotated[str | None, Query(description="ISO datetime")] = None,
    until: Annotated[str | None, Query(description="ISO datetime")] = None,
):
    """История заявок. status=all включает открытые и исполненные."""
    api_key, secret_key = _wallet_keys(user, x_wallet_secret)
    result = await alpaca.get_orders(
        api_key, secret_key,
        status=status, limit=limit,
        after=after, until=until,
    )
    if not result.ok:
        raise _alpaca_error(result)
    return result.data


@router.get("/wallet/history", summary="Equity curve портфеля (Alpaca)")
async def get_wallet_history(
    user: CurrentUserDep,
    x_wallet_secret: WalletSecret = None,
    period: Annotated[str, Query(description="1D | 1W | 1M | 3M | 1A")] = "1M",
    timeframe: Annotated[str, Query(description="1Min | 5Min | 1H | 1D")] = "1D",
):
    """
    Исторические данные стоимости портфеля для графика доходности.
    Возвращает список точек: timestamp, equity, profit_loss, profit_loss_pct.
    """
    api_key, secret_key = _wallet_keys(user, x_wallet_secret)
    result = await alpaca.get_portfolio_history(
        api_key, secret_key,
        period=period, timeframe=timeframe,
    )
    if not result.ok:
        raise _alpaca_error(result)

    data = result.data
    timestamps = data.get("timestamp", [])
    equity = data.get("equity", [])
    profit_loss = data.get("profit_loss", [])
    profit_loss_pct = data.get("profit_loss_pct", [])

    return {
        "base_value": data.get("base_value"),
        "timeframe": data.get("timeframe"),
        "points": [
            {
                "timestamp": timestamps[i],
                "equity": equity[i] if i < len(equity) else None,
                "profit_loss": profit_loss[i] if i < len(profit_loss) else None,
                "profit_loss_pct": profit_loss_pct[i] if i < len(profit_loss_pct) else None,
            }
            for i in range(len(timestamps))
        ],
    }