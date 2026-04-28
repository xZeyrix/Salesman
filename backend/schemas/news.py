from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_serializer, computed_field


class NewsResponse(BaseModel):
    ticker: Optional[str]
    headline: str
    summary: Optional[str]
    source: Optional[str]
    url: Optional[str]
    image: Optional[str]
    category: Optional[str]

    # В модели поле называется related_symbols (list[str]), отдаём на фронт как строку
    related_symbols: list[str] = []

    # published_at -> datetime, отдаём unix-timestamp для фронта
    published_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @computed_field  # type: ignore[misc]
    @property
    def datetime_unix(self) -> int:
        return int(self.published_at.timestamp())

    @computed_field  # type: ignore[misc]
    @property
    def related(self) -> Optional[str]:
        """Удобная строка тикеров для фронта: 'AAPL,MSFT'"""
        return ",".join(self.related_symbols) if self.related_symbols else None