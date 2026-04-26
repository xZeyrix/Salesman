from .config import settings
import finnhub
import asyncio

finnhub_client = finnhub.Client(api_key=settings.finnhub_token)

async def get_symbol(name: str) -> str | None:
    response = await asyncio.to_thread(finnhub_client.symbol_lookup, name)
    if response.get("result"):
        symbol = response["result"][0]["symbol"]
        return symbol
    else:
        return None

async def get_quote(name: str) -> dict | None:
    try:
        response = await asyncio.to_thread(finnhub_client.quote, name)
    except finnhub.exceptions.FinnhubAPIException:
        return None
    if (response.get("c") == 0 and response.get("h") == 0 and response.get("l") == 0) or (response.get("o") == 0 and response.get("t") == 0 and response.get("d") == None and response.get("dp") == None):
        return None
    return response

async def get_recommendations(name: str) -> dict | None:
    try:
        return await asyncio.to_thread(finnhub_client.recommendation_trends, name)
    except finnhub.exceptions.FinnhubAPIException:
        return None

response = asyncio.run(get_recommendations("GOLD"))
print(response)