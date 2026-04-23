from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NewsResponse(BaseModel):
    ticker: Optional[str]
    headline: str
    summary: Optional[str]
    datetime_unix: int
    source: str
    url: Optional[str]
    image: Optional[str]
    category: Optional[str]
    related: Optional[str]

    model_config = ConfigDict(from_attributes=True)

    # ticker: ну название акции хз пусть будет 
    # headline (Заголовок) — крупным шрифтом.
    # summary (Описание) — основной текст.
    # datetime_unix — для отображения времени (например, "5 минут назад").
    # source — чтобы пользователь понимал, откуда инфа.
    # url — чтобы можно было кликнуть и прочитать статью полностью.
    # image — для визуализации (если null, ставь заглушку с логотипом компании).
    # category — для фильтрации (например, вкладки "Крипта", "Слияния").
    # related — чтобы подсветить тикеры компаний прямо в карточке.
