import logging

from fastapi import APIRouter, Body, HTTPException, Query
from sqlalchemy import select

from backend.schemas.wallet import WalletCreate, WalletUpdate, WalletRead
from backend.api.deps import CurrentUserDep
from backend.models.model import Wallet
from backend.core.database import DBSessionDep
from typing import Annotated
from backend.services.alpaca import alpaca

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/wallet', tags=['Кошелек'])


async def _get_wallet_or_404(user: CurrentUserDep, session: DBSessionDep) -> Wallet:
    result = await session.execute(
        select(Wallet).where(Wallet.user_id == user.id)
    )
    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail='Кошелек не найден')
    return wallet


def _check_wallet_keys(wallet: Wallet) -> tuple[str, str]:
    """Проверяет наличие ключей и возвращает (api_key, secret_key)."""
    if not wallet.wallet_src:
        raise HTTPException(
            status_code=400,
            detail="Кошелёк Alpaca не привязан. Добавьте через POST /wallet/create.",
        )
    if not wallet.wallet_key:
        raise HTTPException(
            status_code=400,
            detail="API-ключ отсутствует. Обновите через PATCH /wallet/update.",
        )
    if not wallet._wallet_secret:
        raise HTTPException(
            status_code=400,
            detail="Секретный ключ отсутствует. Обновите через PATCH /wallet/update.",
        )
    return wallet.wallet_key, wallet.wallet_secret


def _alpaca_error(result) -> HTTPException:
    msg = result.error.message if result.error else "неизвестная ошибка"
    code = result.error.code if result.error else 502
    status = 401 if code == 401 else 502
    return HTTPException(status_code=status, detail=f"Ошибка Alpaca: {msg}")


@router.post('/create')
async def wallet_create(
    data: Annotated[WalletCreate, Body()],
    user: CurrentUserDep,
    session: DBSessionDep,
) -> WalletRead:
    try:
        wallet = Wallet(user_id=user.id, **data.model_dump())
        session.add(wallet)
        await session.commit()
        await session.refresh(wallet)
        logger.info(f"Кошелёк создан: user_id={user.id}")
        return wallet
    except Exception as e:
        await session.rollback()
        logger.error(f"wallet_create error user_id={user.id}: {e}")
        raise HTTPException(status_code=500, detail='Не удалось сохранить данные')


@router.get('/read')
async def wallet_read(
    session: DBSessionDep,
    user: CurrentUserDep,
) -> WalletRead:
    try:
        wallet = await _get_wallet_or_404(user, session)
        return wallet
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"wallet_read error user_id={user.id}: {e}")
        raise HTTPException(status_code=500, detail='Не удалось получить данные')


@router.patch('/update')
async def wallet_update(
    data: Annotated[WalletUpdate, Body()],
    user: CurrentUserDep,
    session: DBSessionDep,
) -> WalletRead:
    try:
        wallet = await _get_wallet_or_404(user, session)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(wallet, key, value)

        await session.commit()
        await session.refresh(wallet)
        logger.info(f"Кошелёк обновлён: user_id={user.id}")
        return wallet
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"wallet_update error user_id={user.id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обновлении данных")


@router.delete('/delete')
async def wallet_delete(
    user: CurrentUserDep,
    session: DBSessionDep,
):
    try:
        wallet = await _get_wallet_or_404(user, session)
        await session.delete(wallet)
        await session.commit()
        logger.info(f"Кошелёк удалён: user_id={user.id}")
        return {"detail": "Кошелек успешно удален"}
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"wallet_delete error user_id={user.id}: {e}")
        raise HTTPException(status_code=500, detail="Не удалось удалить кошелек")


@router.get("/account", summary="Баланс счёта Alpaca")
async def get_wallet_account(user: CurrentUserDep, session: DBSessionDep):
    try:
        wallet = await _get_wallet_or_404(user, session)
        api_key, secret_key = _check_wallet_keys(wallet)
    except HTTPException:
        raise

    result = await alpaca.get_account(api_key, secret_key)
    if not result.ok:
        logger.warning(f"Alpaca account error user_id={user.id}: {result.error}")
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


@router.get("/positions", summary="Открытые позиции / портфель (Alpaca)")
async def get_wallet_positions(user: CurrentUserDep, session: DBSessionDep):
    try:
        wallet = await _get_wallet_or_404(user, session)
        api_key, secret_key = _check_wallet_keys(wallet)
    except HTTPException:
        raise

    result = await alpaca.get_positions(api_key, secret_key)
    if not result.ok:
        logger.warning(f"Alpaca positions error user_id={user.id}: {result.error}")
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


@router.get("/trades", summary="История исполненных сделок (Alpaca)")
async def get_wallet_trades(
    user: CurrentUserDep,
    session: DBSessionDep,
    page_size: Annotated[int, Query(ge=1, le=200)] = 50,
    after: Annotated[str | None, Query(description="ISO: 2024-01-01T00:00:00Z")] = None,
    until: Annotated[str | None, Query(description="ISO: 2024-12-31T23:59:59Z")] = None,
):
    try:
        wallet = await _get_wallet_or_404(user, session)
        api_key, secret_key = _check_wallet_keys(wallet)
    except HTTPException:
        raise

    result = await alpaca.get_activities(
        api_key, secret_key,
        activity_type="FILL",
        page_size=page_size,
        after=after,
        until=until,
    )
    if not result.ok:
        logger.warning(f"Alpaca trades error user_id={user.id}: {result.error}")
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


@router.get("/orders", summary="История ордеров (Alpaca)")
async def get_wallet_orders(
    user: CurrentUserDep,
    session: DBSessionDep,
    status: Annotated[str, Query(description="open | closed | all")] = "all",
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    after: Annotated[str | None, Query(description="ISO datetime")] = None,
    until: Annotated[str | None, Query(description="ISO datetime")] = None,
):
    try:
        wallet = await _get_wallet_or_404(user, session)
        api_key, secret_key = _check_wallet_keys(wallet)
    except HTTPException:
        raise

    result = await alpaca.get_orders(
        api_key, secret_key,
        status=status, limit=limit,
        after=after, until=until,
    )
    if not result.ok:
        logger.warning(f"Alpaca orders error user_id={user.id}: {result.error}")
        raise _alpaca_error(result)

    return result.data


@router.get("/history", summary="Equity curve портфеля (Alpaca)")
async def get_wallet_history(
    user: CurrentUserDep,
    session: DBSessionDep,
    period: Annotated[str, Query(description="1D | 1W | 1M | 3M | 1A")] = "1M",
    timeframe: Annotated[str, Query(description="1Min | 5Min | 1H | 1D")] = "1D",
):
    try:
        wallet = await _get_wallet_or_404(user, session)
        api_key, secret_key = _check_wallet_keys(wallet)
    except HTTPException:
        raise

    result = await alpaca.get_portfolio_history(
        api_key, secret_key,
        period=period, timeframe=timeframe,
    )
    if not result.ok:
        logger.warning(f"Alpaca history error user_id={user.id}: {result.error}")
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