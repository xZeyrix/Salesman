from typing import Annotated
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class Mode(str, Enum):
    DEFAULT = 'default'
    STOCKS = 'stocks'

class Role(str, Enum):
    USER = 'user'
    AI = 'ai'

class MessageRequest(BaseModel):
    text: Annotated[str, Field(min_length=1, max_length=1000)]

class MessageResponse(BaseModel):
    role: Role
    text: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

