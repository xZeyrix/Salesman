from aiogram.types import Message, Voice, PhotoSize, Document
from typing import Optional, Union, Literal
from ai_system.type_helpers import CoreResponse, SalesmanResponse, ContentStructure, IncMsgStructure
from ai_system.converters.document_to_text import convert as doc_to_text
from ai_system.converters.photo_to_text import convert as ph_to_text
from ai_system.converters.voice_to_text import convert as vc_to_text
from ai_system.converters.text_to_text import convert as text_to_text
import re
import inspect
from pydantic import ValidationError

class NormalizeMsgStructure:
    def normalize(self, object: Union[Message, IncMsgStructure, dict]) -> IncMsgStructure:
        if not isinstance(object, (Message, IncMsgStructure, dict)):
            raise TypeError('Invalid type. Try AiogramMessage / IncMsgStructure / JSON exactly {"id": int, "text": str (optionally), "file_id": str (optionally), "content_type": str}.')
        
        if isinstance(object, Message):
            text = object.text or object.caption or None
            if object.voice:
                file_id = object.voice.file_id
            elif object.photo:
                file_id = object.photo[-1].file_id
            elif object.document:
                file_id = object.document.file_id
            else:
                file_id = None

            data = IncMsgStructure(
                user_id=object.from_user.id,
                history=None,
                text=text,
                file_id=file_id,
                content_type=object.content_type
            )
            return data
        
        if isinstance(object, IncMsgStructure):
            return object
        try:
            return IncMsgStructure(**object)
        except ValidationError as e:
            raise TypeError(f'The JSON that you provided is invalid. The format must be exactly: {IncMsgStructure.model_json_schema()}')

class ContentProcessor:
    async def process(self, data: IncMsgStructure) -> str:
        types = {
            "text": lambda: text_to_text(data.text),
            "voice": lambda: vc_to_text(data.file_id, data.text),
            "photo": lambda: ph_to_text(data.file_id, data.text),
            "document": lambda: doc_to_text(data.file_id, data.text),
        }
        if data.content_type not in types.keys():
            raise ValueError(f"The 'content_type' value is invalid. It can be only one of these values: {types.keys()}.")
        result = types[data.content_type]()
        if inspect.isawaitable(result):
            return await result
        return result
        

class TextNormalizer:
    def clean(self, text: str) -> str:
        return re.sub(r"[^a-zA-Zа-яА-ЯёЁ.,:\-()1234567890?! ]", "", text).strip()

class BotCore:
    def respond(self, text: str, history: Optional[str] = None) -> CoreResponse:
        return CoreResponse(history=history, response=text)

class Salesman:
    def __init__(self):
        self.adapter = NormalizeMsgStructure()
        self.processor = ContentProcessor()
        self.normalizer = TextNormalizer()
        self.core = BotCore()

    async def handle(self, object: Union[Message, IncMsgStructure, dict]) -> SalesmanResponse:
        try:
            data = self.adapter.normalize(object)
            user_text = await self.processor.process(data)
            clean = self.normalizer.clean(user_text)

            id = data.user_id
            response = self.core.respond(clean, data.history)
            text = response.response
            history = response.history
            return SalesmanResponse(status="OK", content=ContentStructure(user_id=id, history=history, response=text))
        except Exception as e:
            return SalesmanResponse(status=f"ERROR: {e}", content=None)