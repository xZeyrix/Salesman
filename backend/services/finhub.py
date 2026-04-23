import asyncio
import logging
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import httpx
from backend.core.config import settings
from backend.models.model import News  

logger = logging.getLogger("NewsWorker")

engine = create_async_engine(str(settings.DB_URL))
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class NewsCollector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1/news"
        self.categories = ["general", "forex", "crypto", "merger"]

    async def fetch_and_save(self):
        async with httpx.AsyncClient(timeout=15.0) as client:
            for category in self.categories:
                try:
                    logger.info(f"Запрос новостей категории: {category}")
                    response = await client.get(
                        self.base_url, 
                        params={'category': category, 'token': self.api_key}
                    )
                    
                    if response.status_code == 429:
                        logger.warning("Лимит запросов превышен. Ждем...")
                        break
                    
                    response.raise_for_status()
                    data = response.json()

                    if data:
                        await self._process_batch(data)
                        
                except Exception as e:
                    logger.error(f"Ошибка при сборе {category}: {e}")
                
                await asyncio.sleep(1)

    async def _process_batch(self, news_items: list):
        async with async_session() as session:
            try:
                for item in news_items:
                    dt_obj = datetime.fromtimestamp(item.get('datetime'))
                    
                    stmt = insert(News).values(
                        finhub_id=item['id'],
                        category=item.get('category'),
                        headline=item.get('headline'),
                        summary=item.get('summary'),
                        source=item.get('source'),
                        url=item.get('url'),
                        image=item.get('image'),
                        related=item.get('related'), 
                        datetime_unix=item.get('datetime'),
                    )
                    
                    # Если ID уже есть — ничего не делаем
                    stmt = stmt.on_conflict_do_nothing(index_elements=['finhub_id'])
                    await session.execute(stmt)
                
                await session.commit()
                logger.info(f"Сохранено/обработано {len(news_items)} новостей.")
            except Exception as e:
                logger.error(f"Ошибка сохранения в БД: {e}")
                await session.rollback()

async def start_worker():
    collector = NewsCollector(api_key=settings.FINHUB_KEY)
    logger.info("Воркер запущен...")
    
    while True:
        await collector.fetch_and_save()
        logger.info("Цикл завершен. Спим 120 секунд...")
        await asyncio.sleep(120)
