import asyncio

from ai_system.salesman import Salesman
from ai_system.type_helpers import IncMsgStructure, SalesmanResponse
from ai_system.tests.utils import Cassette


def test_salesman_handle_cached() -> None:
    cassette = Cassette()
    ai = Salesman()
    data = IncMsgStructure(user_id=1, content_type="text", text="hello")

    payload = {"user_id": data.user_id, "content_type": data.content_type, "text": data.text}

    async def run() -> dict:
        response = await ai.handle(data)
        return response.model_dump()

    cached = asyncio.run(cassette.async_get_or_set("salesman_handle_text", payload, run))
    response = SalesmanResponse(**cached)

    assert response.status == "OK"
    assert response.content is not None
    assert response.content.user_id == data.user_id
    assert response.content.response
