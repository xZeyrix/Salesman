import asyncio
import pytest

from ai_system.salesman import ContentProcessor
from ai_system.type_helpers import IncMsgStructure
from ai_system.tests.utils import Cassette


def test_content_processor_text_cached() -> None:
    cassette = Cassette()
    processor = ContentProcessor()
    data = IncMsgStructure(user_id=1, content_type="text", text="hello")

    payload = {"content_type": data.content_type, "text": data.text}

    async def run() -> str:
        return await processor.process(data)

    result = asyncio.run(cassette.async_get_or_set("content_text", payload, run))
    assert isinstance(result, str)
    assert result


def test_content_processor_voice_cached() -> None:
    cassette = Cassette()
    processor = ContentProcessor()
    data = IncMsgStructure(user_id=1, content_type="voice", file_id="file123", text="hi")

    payload = {
        "content_type": data.content_type,
        "file_id": data.file_id,
        "text": data.text,
    }

    async def run() -> str:
        return await processor.process(data)

    result = asyncio.run(cassette.async_get_or_set("content_voice", payload, run))
    assert isinstance(result, str)
    assert result


def test_content_processor_photo_cached() -> None:
    cassette = Cassette()
    processor = ContentProcessor()
    data = IncMsgStructure(user_id=1, content_type="photo", file_id="file123", text="hi")

    payload = {
        "content_type": data.content_type,
        "file_id": data.file_id,
        "text": data.text,
    }

    async def run() -> str:
        return await processor.process(data)

    result = asyncio.run(cassette.async_get_or_set("content_photo", payload, run))
    assert isinstance(result, str)
    assert result


def test_content_processor_document_cached() -> None:
    cassette = Cassette()
    processor = ContentProcessor()
    data = IncMsgStructure(user_id=1, content_type="document", file_id="doc123", text="hi")

    payload = {
        "content_type": data.content_type,
        "file_id": data.file_id,
        "text": data.text,
    }

    async def run() -> str:
        return await processor.process(data)

    result = asyncio.run(cassette.async_get_or_set("content_document", payload, run))
    assert isinstance(result, str)
    assert result


def test_content_processor_invalid_content_type() -> None:
    processor = ContentProcessor()
    data = IncMsgStructure(user_id=1, content_type="bad")

    with pytest.raises(ValueError):
        asyncio.run(processor.process(data))
