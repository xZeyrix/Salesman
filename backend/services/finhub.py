import httpx
from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import insert
from backend.core.config import settings
from backend.core.database import get_session
from backend.models.models import StockNews # проверь путь к файлу с моделями
import logging
logger = logging.getLogger(__name__)

class FinhubNews:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://finnhub.io"

    async def save_news_to_db(self, news_list: list, ticker: str):
        """Асинхронное сохранение новостей в базу с защитой от дублей"""
        if not news_list:
            return

        async for session in get_session(): # Используем твой генератор сессий
            try:
                for item in news_list:
                    # Создаем запрос вставки для PostgreSQL
                    stmt = insert(StockNews).values(
                        id=item['id'],
                        ticker=ticker.upper(),
                        category=item.get('category'),
                        headline=item.get('headline'),
                        image=item.get('image'),
                        related=item.get('related'),
                        source=item.get('source'),
                        summary=item.get('summary'),
                        url=item.get('url'),
                        datetime_unix=item.get('datetime')
                    )
                    
                    stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
                    await session.execute(stmt)
                
                await session.commit()
            except Exception as e:
                logger.error(f"Ошибка при сохранении новости в бд: {e}")
                await session.rollback()
            break

    async def fetch_and_sync_news(self, ticker: str, days: int = 1):
        """Получает новости из API и синхронизирует их с БД"""
        ticker = ticker.upper()
        now = datetime.now()
        from_date = (now - timedelta(days=days)).strftime('%Y-%m-%d')
        to_date = now.strftime('%Y-%m-%d')

        params = {
            'symbol': ticker,
            'from': from_date,
            'to': to_date,
            'token': self.api_key
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code == 429:
                    print("Rate limit reached")
                    return []
                
                response.raise_for_status()
                data = response.json()

                if data:
                    # Сохраняем в БД в фоновом режиме (опционально)
                    await self.save_news_to_db(data, ticker)
                
                return data

            except Exception as e:
                print(f"Finnhub Request Error: {e}")
                return []

news_service = FinhubNews(api_key=settings.FINHUB_KEY)