from pydantic.dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional, Literal

class ContentStructure(BaseModel):
    user_id: int
    history: Optional[str]
    response: str

class CoreResponse(BaseModel):
    history: Optional[str]
    response: str

class SalesmanResponse(BaseModel):
    status: str
    content: Optional[ContentStructure]

class IncMsgStructure(BaseModel):
    user_id: int
    history: Optional[str] = None
    text: Optional[str] = None
    file_id: Optional[str] = None
    content_type: str

class RouterResponse(BaseModel):
    type: str
    subtype: str
    name: str | None

class ReduceHistoryResponse(BaseModel):
    status: Literal["OK", "ERROR"]
    history: str | None

class PromptInjectionError(Exception):
    pass