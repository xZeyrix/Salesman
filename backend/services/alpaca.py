"""
Async-клиент Alpaca Markets API.

Документация: https://docs.alpaca.markets/

Аутентификация — два заголовка на каждый запрос:
  APCA-API-KEY-ID:     <api_key>
  APCA-API-SECRET-KEY: <secret_key>

Никакого HMAC. Ключи пользователя:
  api_key    → User.wallet_key
  secret_key → заголовок X-Wallet-Secret (не хранится в БД)

Базовые URL:
  Trading:  https://api.alpaca.markets/v2
  Paper:    https://paper-api.alpaca.markets/v2  (для тестов)
  News:     https://data.alpaca.markets/v1beta1
"""

import logging
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)

TRADING_BASE = "https://api.alpaca.markets/v2"
DATA_BASE = "https://data.alpaca.markets/v1beta1"


# ──────────────────────────────────────────────
# Результирующий тип
# ──────────────────────────────────────────────

@dataclass
class AlpacaError:
    code: int
    message: str


@dataclass
class AlpacaResult:
    ok: bool
    data: Any
    error: AlpacaError | None = None


# ──────────────────────────────────────────────
# Клиент
# ──────────────────────────────────────────────

class AlpacaClient:
    """
    Stateless async-клиент Alpaca Markets.
    Один экземпляр обслуживает всех пользователей —
    ключи передаются в каждый вызов.
    """

    def __init__(self, timeout: float = 10.0):
        self._timeout = timeout

    def _headers(self, api_key: str, secret_key: str) -> dict:
        return {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key,
            "Accept": "application/json",
        }

    async def _get(
        self,
        base: str,
        path: str,
        api_key: str,
        secret_key: str,
        params: dict | None = None,
    ) -> AlpacaResult:
        url = f"{base}{path}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    url,
                    headers=self._headers(api_key, secret_key),
                    params=params,
                )
                if response.status_code == 401:
                    return AlpacaResult(
                        ok=False, data=None,
                        error=AlpacaError(401, "Неверные ключи Alpaca"),
                    )
                if response.status_code == 403:
                    return AlpacaResult(
                        ok=False, data=None,
                        error=AlpacaError(403, "Доступ запрещён"),
                    )
                response.raise_for_status()
                return AlpacaResult(ok=True, data=response.json())

        except httpx.HTTPStatusError as e:
            logger.error(f"Alpaca HTTP {e.response.status_code} [{path}]")
            return AlpacaResult(
                ok=False, data=None,
                error=AlpacaError(e.response.status_code, str(e)),
            )
        except Exception as e:
            logger.error(f"Alpaca request error [{path}]: {e}")
            return AlpacaResult(
                ok=False, data=None,
                error=AlpacaError(-1, str(e)),
            )

    # ── Кошелёк ────────────────────────────────

    async def get_account(self, api_key: str, secret_key: str) -> AlpacaResult:
        """
        Баланс и сводка по счёту.
        GET /v2/account
        Возвращает: equity, cash, buying_power, portfolio_value, ...
        """
        return await self._get(TRADING_BASE, "/account", api_key, secret_key)

    async def get_positions(self, api_key: str, secret_key: str) -> AlpacaResult:
        """
        Текущие открытые позиции (портфель).
        GET /v2/positions
        Возвращает список: symbol, qty, current_price, market_value, unrealized_pl, ...
        """
        return await self._get(TRADING_BASE, "/positions", api_key, secret_key)

    async def get_portfolio_history(
        self,
        api_key: str,
        secret_key: str,
        period: str = "1M",        # 1D, 1W, 1M, 3M, 1A
        timeframe: str = "1D",     # 1Min, 5Min, 15Min, 1H, 1D
    ) -> AlpacaResult:
        """
        Историческая доходность портфеля (equity curve).
        GET /v2/account/portfolio/history
        """
        return await self._get(
            TRADING_BASE, "/account/portfolio/history",
            api_key, secret_key,
            params={"period": period, "timeframe": timeframe},
        )

    async def get_orders(
        self,
        api_key: str,
        secret_key: str,
        status: str = "all",   # open | closed | all
        limit: int = 50,
        after: str | None = None,   # ISO datetime
        until: str | None = None,
    ) -> AlpacaResult:
        """
        История заявок (ордеров).
        GET /v2/orders
        """
        params: dict = {"status": status, "limit": limit, "direction": "desc"}
        if after:
            params["after"] = after
        if until:
            params["until"] = until
        return await self._get(TRADING_BASE, "/orders", api_key, secret_key, params)

    async def get_activities(
        self,
        api_key: str,
        secret_key: str,
        activity_type: str = "FILL",   # FILL = исполненные сделки
        page_size: int = 50,
        after: str | None = None,
        until: str | None = None,
    ) -> AlpacaResult:
        """
        История активностей счёта — сделки, дивиденды, пополнения.
        GET /v2/account/activities/{activity_type}
        activity_type=FILL → только исполненные сделки
        """
        params: dict = {"page_size": page_size, "direction": "desc"}
        if after:
            params["after"] = after
        if until:
            params["until"] = until
        return await self._get(
            TRADING_BASE,
            f"/account/activities/{activity_type}",
            api_key, secret_key,
            params,
        )


# Singleton
alpaca = AlpacaClient()
