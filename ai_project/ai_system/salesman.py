from aiogram.types import Message, Voice, PhotoSize, Document
from typing import Optional, Union, Literal
from ai_system.type_helpers import CoreResponse, SalesmanResponse, ContentStructure, IncMsgStructure
import re

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
        return IncMsgStructure(**object)

class ContentProcessor:
    def process(self, data: IncMsgStructure) -> str:
        if data.content_type == "text":
            return self._text(data.text)
        elif data.content_type == "voice":
            return self._voice_to_text(data.file_id, data.text)
        elif data.content_type == "photo":
            return self._image_to_text(data.file_id, data.text)
        elif data.content_type == "document":
            return self._document_to_text(data.file_id, data.text)

    def _text(self, text: str) -> str:
        if text:
            return text
        raise ValueError("Text cannot be empty if content_type is 'text'")

    def _voice_to_text(self, voice: str, text: Optional[str] = None) -> str:
        if voice:
            return "распознанный текст"
        raise ValueError("File_id cannot be empty if content_type is 'voice'")

    def _image_to_text(self, image: str, text: Optional[str] = None) -> str:
        if image:
            return f"Описание фото: {None}, Запрос пользователя: {text}"
        raise ValueError("File_id cannot be empty if content_type is 'image'")
    
    def _document_to_text(self, document: str, text: Optional[str] = None) -> str:
        if document:
            return "текст документа"
        raise ValueError("File_id cannot be empty if content_type is 'document'")

class TextNormalizer:
    def clean(self, text: str) -> str:
        return re.sub(r"[^a-zA-Zа-яА-ЯёЁ.,:\-()1234567890?! ]", "", text).strip()

class BotCore:
    def respond(self, text: str, history: Optional[str] = None) -> CoreResponse:
        return CoreResponse(history, text)

class Salesman:
    def __init__(self):
        self.adapter = NormalizeMsgStructure()
        self.processor = ContentProcessor()
        self.normalizer = TextNormalizer()
        self.core = BotCore()

    def handle(self, object: Union[Message, IncMsgStructure, dict]) -> SalesmanResponse:
        try:
            data = self.adapter.normalize(object)
            user_text = self.processor.process(data)
            clean = self.normalizer.clean(user_text)

            id = data.user_id
            response = self.core.respond(clean, data.history)
            text = response.response
            history = response.history
            return SalesmanResponse("OK", ContentStructure(id, history, text))
        except Exception as e:
            return SalesmanResponse(f"ERROR: {e}", None)