from aiogram.types import Message, Voice, PhotoSize, Document
from typing import Optional, Union, Literal
from .type_helpers import CoreResponse, SalesmanResponse, ContentStructure, IncMsgStructure, RouterResponse, ReduceHistoryResponse
from .converters.document_to_text import convert as doc_to_text
from .converters.photo_to_text import convert as ph_to_text
from .converters.voice_to_text import convert as vc_to_text
from .converters.text_to_text import convert as text_to_text
import re
import inspect
from pydantic import ValidationError
from .groq_functions import PromptGuard, AiRouter, AiSalesman, ReduceHistory
from .config import prompts

class NormalizeMsgStructure:
    def normalize(self, object: Union[Message, IncMsgStructure, dict]) -> IncMsgStructure:
        if not isinstance(object, (Message, IncMsgStructure, dict)):
            raise TypeError('Invalid type. Try AiogramMessage / IncMsgStructure / JSON exactly {"id": int, "text": str (optionally), "file_id": str (optionally), "content_type": str}.')
        
        if isinstance(object, Message):
            text = object.text or object.caption or None
            file_ids = {
                "voice": object.voice.file_id if object.voice else None,
                "photo": object.photo[-1].file_id if object.photo else None,
                "document": object.document.file_id if object.document else None,
            }
            if object.content_type in file_ids:
                file_id = file_ids[object.content_type]
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
        if data.content_type != "text":
            raise ValueError("At the moment 'content_type' field cannot be anything except 'text'.")
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
        return re.sub(r"[^a-zA-Zа-яА-ЯёЁ.,:\-()1234567890?!_ ]", "", text).strip()

class BotCore:
    async def _is_prompt_injection(self, user_message: str, sensetivity: float | None = None) -> bool:
        guard = PromptGuard(user_message, sensetivity)
        response = await guard.is_injection()
        return response
    async def _get_route(self, user_message: str, prompt: str, history: str | None = None) -> RouterResponse:
        router = AiRouter(user_message, history)
        response = await router.get_route(prompt)
        return response
    async def _get_response(self, user_message: str, prompt: str, history: str | None = None, data: str | None = None) -> str:
        salesman = AiSalesman(user_message, history, data)
        response = await salesman.get_response(prompt)
        return response
    async def _reduce_history(self, user_message: str, history: str, ai_message: str, prompt: str) -> ReduceHistoryResponse:
        reduce_history = ReduceHistory(user_message, history)
        response = await reduce_history.compress(ai_message, prompt)
        return response
    async def respond(self, user_message: str, history: str | None = None) -> CoreResponse:
        await self._is_prompt_injection(user_message)
        await self._get_route(user_message, prompts.router, history)
        await self._get_response(user_message, prompts.salesman, history)
        await self._reduce_history(user_message, history, "Принято.", prompts.history)
        return CoreResponse(history=history, response=user_message)

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
            response = await self.core.respond(clean, data.history)
            text = response.response
            history = response.history
            return SalesmanResponse(status="OK", content=ContentStructure(user_id=id, history=history, response=text))
        except Exception as e:
            return SalesmanResponse(status=f"ERROR: {e}", content=None)