from pydantic import BaseModel, Field

class NewsResponse(BaseModel):
    ticker: str = Field(max_length=20)
    content: str

