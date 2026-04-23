import pytest

from ai_system.salesman import NormalizeMsgStructure
from ai_system.type_helpers import IncMsgStructure


def test_normalize_dict() -> None:
    data = {"user_id": 1, "text": "hello", "file_id": None, "content_type": "text"}
    result = NormalizeMsgStructure().normalize(data)
    assert isinstance(result, IncMsgStructure)
    assert result.user_id == 1
    assert result.text == "hello"
    assert result.file_id is None
    assert result.content_type == "text"


def test_normalize_inc_msg_structure() -> None:
    inc = IncMsgStructure(user_id=2, content_type="text", text="ping")
    result = NormalizeMsgStructure().normalize(inc)
    assert result is inc


def test_normalize_invalid_type() -> None:
    with pytest.raises(TypeError):
        NormalizeMsgStructure().normalize(12345)
