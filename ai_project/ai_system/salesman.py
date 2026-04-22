from aiogram.types import Message
import re

class TelegramAdapter:
    def extract(self, message: Message):
        if message.text:
            return {"type": "text", "content": message.text}
        elif message.voice:
            return {"type": "voice", "content": message.voice}
        elif message.photo:
            return {"type": "image", "content": message.photo}
        elif message.document:
            return {"type": "document", "content": message.document}

class ContentProcessor:
    def process(self, data: dict):
        if data["type"] == "text":
            return data["content"]
        elif data["type"] == "voice":
            return self._voice_to_text(data["content"])
        elif data["type"] == "image":
            return self._image_to_text(data["content"])
        elif data["type"] == "document":
            return self._document_to_text(data["content"])

    def _voice_to_text(self, voice):
        return "распознанный текст"

    def _image_to_text(self, image):
        return "текст с картинки"
    
    def _document_to_text(self, document):
        return "текст документа"

class TextNormalizer:
    def clean(self, text):
        return re.sub(r"[^a-zA-Zа-яА-ЯёЁ.,:\-()1234567890?! ]", "", text).strip()

class BotCore:
    def respond(self, text):
        return "ответ на: " + text

class Salesman:
    def __init__(self):
        self.adapter = TelegramAdapter()
        self.processor = ContentProcessor()
        self.normalizer = TextNormalizer()
        self.core = BotCore()

    def handle(self, message: Message):
        data = self.adapter.extract(message)
        text = self.processor.process(data)
        clean = self.normalizer.clean(text)
        return self.core.respond(clean)