from pydantic.dataclasses import dataclass
from typing import Optional, Literal

@dataclass
class ContentStructure:
    id: int
    history: Optional[str]
    response: str


@dataclass
class CoreResponse:
    history: Optional[str]
    response: str

@dataclass
class SalesmanResponse:
    status: str
    content: Optional[ContentStructure]

@dataclass
class IncMsgStructure:
    user_id: int
    history: Optional[str]
    text: Optional[str]
    file_id: Optional[str]
    content_type: Literal["text", "voice", "photo", "document"]