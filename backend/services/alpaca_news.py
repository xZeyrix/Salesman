"""
Фоновый воркер сбора новостей через Alpaca Markets News API.

Заменяет finhub.py полностью.

API: GET https://data.alpaca.markets/v1beta1/news
Документация: https://docs.alpaca.markets/reference/news-3

Особенности Alpaca News:
  - Источник: Benzinga (130+ статей/день)
  - Есть summary, images, symbols (тикеры), author
  - Поддерживает фильтрацию по symbols, start/end дате
  - Пагинация через параметр page_token (next_page_token в ответе)
  - Бесплатный план: неограниченный доступ к новостям

Ключи: серверные (из config) — используем наш ключ для сбора новостей,
а не ключи юзера.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings
from backend.models.model import News

logger = logging.getLogger("AlpacaNewsWorker")

engine = create_async_engine(str(settings.DB_URL))
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

NEWS_URL = "https://data.alpaca.markets/v1beta1/news"

# Тикеры для целевого сбора новостей
WATCHED_TICKERS: list[str] = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
    "NVDA", "META", "JPM", "BAC", "FRHC",
]


def _alpaca_headers() -> dict:
    return {
        "APCA-API-KEY-ID": settings.ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": settings.ALPACA_SECRET_KEY,
        "Accept": "application/json",
    }


class AlpacaNewsCollector:

    async def fetch_news(
        self,
        symbols: list[str] | None = None,
        start: str | None = None,
        end: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """
        Получает новости с пагинацией.
        symbols=None → общие новости без фильтра по тикеру.
        Возвращает все статьи (все страницы).
        """
        params: dict = {"limit": limit, "sort": "desc"}
        if symbols:
            params["symbols"] = ",".join(symbols)
        if start:
            params["start"] = start
        if end:
            params["end"] = end

        all_articles: list[dict] = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            while True:
                try:
                    response = await client.get(
                        NEWS_URL,
                        headers=_alpaca_headers(),
                        params=params,
                    )

                    if response.status_code == 429:
                        logger.warning("Alpaca rate limit. Пауза 30 сек.")
                        await asyncio.sleep(30)
                        continue

                    response.raise_for_status()
                    data = response.json()

                    articles = data.get("news", [])
                    all_articles.extend(articles)

                    # Пагинация
                    next_token = data.get("next_page_token")
                    if not next_token or not articles:
                        break

                    params["page_token"] = next_token
                    await asyncio.sleep(0.3)

                except Exception as e:
                    logger.error(f"Ошибка запроса новостей [{symbols}]: {e}")
                    break

        return all_articles

    async def _save_batch(self, articles: list[dict], ticker: str | None = None):
        """
        Сохраняет статьи в БД.
        Поле ticker — если запрос был по конкретному тикеру.
        У каждой статьи есть поле symbols — список тикеров из Alpaca.
        """
        if not articles:
            return

        async with async_session() as session:
            try:
                saved = 0
                for article in articles:
                    alpaca_id = article.get("id")
                    if not alpaca_id:
                        continue

                    headline = article.get("headline", "").strip()
                    if not headline:
                        continue

                    # Alpaca возвращает symbols как список → берём первый или переданный
                    symbols: list = article.get("symbols", [])
                    article_ticker = ticker or (symbols[0] if symbols else None)

                    # Дата: Alpaca отдаёт ISO строку "2024-01-15T12:00:00Z"
                    created_at_str = article.get("created_at", "")
                    try:
                        dt = datetime.fromisoformat(
                            created_at_str.replace("Z", "+00:00")
                        )
                        datetime_unix = int(dt.timestamp())
                    except Exception:
                        datetime_unix = 0

                    # related: все тикеры статьи через запятую
                    related = ",".join(symbols) if symbols else None

                    stmt = (
                        insert(News)
                        .values(
                            finhub_id=alpaca_id,      # поле переиспользуем как unique id
                            ticker=article_ticker,
                            category=article.get("source", "alpaca"),
                            headline=headline[:500],
                            summary=article.get("summary"),
                            source=article.get("source"),
                            url=article.get("url"),
                            image=(
                                article["images"][0]["url"]
                                if article.get("images")
                                else None
                            ),
                            related=related[:200] if related else None,
                            datetime_unix=datetime_unix,
                        )
                        .on_conflict_do_update(
                            index_elements=["finhub_id"],
                            set_={
                                "ticker": article_ticker,
                                "related": related[:200] if related else None,
                            },
                        )
                    )
                    await session.execute(stmt)
                    saved += 1

                await session.commit()
                label = f"тикер={ticker}" if ticker else "общие"
                logger.info(f"Сохранено {saved} новостей [{label}]")

            except Exception as e:
                logger.error(f"Ошибка записи в БД: {e}")
                await session.rollback()

    async def run_cycle(self):
        """Один полный цикл сбора: по тикерам + общие."""
        now = datetime.now(timezone.utc)
        start = (now - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        # 1. Новости по каждому тикеру
        for ticker in WATCHED_TICKERS:
            articles = await self.fetch_news(
                symbols=[ticker], start=start, end=end, limit=50
            )
            await self._save_batch(articles, ticker=ticker)
            await asyncio.sleep(0.5)   # мягкий rate-limit

        # 2. Общие новости (топ-50 без фильтра)
        articles = await self.fetch_news(start=start, end=end, limit=50)
        await self._save_batch(articles, ticker=None)


# ──────────────────────────────────────────────
# Воркер
# ──────────────────────────────────────────────

async def start_worker():
    collector = AlpacaNewsCollector()
    logger.info("Alpaca News воркер запущен.")
    cycle = 0

    while True:
        cycle += 1
        logger.info(f"=== Цикл #{cycle} ===")
        try:
            await collector.run_cycle()
        except Exception as e:
            logger.error(f"Ошибка в цикле воркера: {e}")

        logger.info("Цикл завершён. Спим 300 сек (5 мин).")
        await asyncio.sleep(300)
