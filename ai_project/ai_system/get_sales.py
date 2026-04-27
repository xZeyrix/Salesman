from .config import settings
import finnhub
import asyncio
from datetime import datetime

finnhub_client = finnhub.Client(api_key=settings.finnhub_token)


def _split_names(name: str) -> list[str]:
    return [item.strip() for item in name.split(",") if item.strip()]


async def _resolve_symbols(name: str) -> list[str]:
    symbols = []
    for item in _split_names(name):
        symbol = await get_symbol(item)
        if symbol:
            symbols.append(symbol)
    return symbols

async def get_symbol(name: str) -> str | None:
    response = await asyncio.to_thread(finnhub_client.symbol_lookup, name)
    if response.get("result"):
        symbol = response["result"][0]["symbol"]
        return symbol
    else:
        return None

async def get_quote(name: str, since: str, until: str) -> dict | None:
    symbols = await _resolve_symbols(name)
    if not symbols:
        return None

    if len(symbols) == 1:
        try:
            response = await asyncio.to_thread(finnhub_client.quote, symbols[0])
        except finnhub.exceptions.FinnhubAPIException:
            return None
        if (response.get("c") == 0 and response.get("h") == 0 and response.get("l") == 0) or (response.get("o") == 0 and response.get("t") == 0 and response.get("d") == None and response.get("dp") == None):
            return None
        return response

    out = {}
    for symbol in symbols:
        try:
            response = await asyncio.to_thread(finnhub_client.quote, symbol)
        except finnhub.exceptions.FinnhubAPIException:
            out[symbol] = None
            continue
        if (response.get("c") == 0 and response.get("h") == 0 and response.get("l") == 0) or (response.get("o") == 0 and response.get("t") == 0 and response.get("d") == None and response.get("dp") == None):
            out[symbol] = None
        else:
            out[symbol] = response
    return out

async def get_recommendations(name: str, since: str, until: str) -> dict | None:
    symbols = await _resolve_symbols(name)
    if not symbols:
        return None

    if len(symbols) == 1:
        try:
            return await asyncio.to_thread(finnhub_client.recommendation_trends, symbols[0])
        except finnhub.exceptions.FinnhubAPIException:
            return None

    out = {}
    for symbol in symbols:
        try:
            out[symbol] = await asyncio.to_thread(finnhub_client.recommendation_trends, symbol)
        except finnhub.exceptions.FinnhubAPIException:
            out[symbol] = None
    return out

async def get_surprise(name: str, since: str, until: str) -> dict | None:
    symbols = await _resolve_symbols(name)
    if not symbols:
        return None

    if len(symbols) == 1:
        try:
            return await asyncio.to_thread(finnhub_client.company_earnings, symbols[0])
        except finnhub.exceptions.FinnhubAPIException:
            return None

    out = {}
    for symbol in symbols:
        try:
            out[symbol] = await asyncio.to_thread(finnhub_client.company_earnings, symbol)
        except finnhub.exceptions.FinnhubAPIException:
            out[symbol] = None
    return out
    
async def get_calendar(name: str, since: str, until: str) -> dict | None:
    symbols = await _resolve_symbols(name)
    if not symbols:
        return None

    if len(symbols) == 1:
        try:
            return await asyncio.to_thread(finnhub_client.earnings_calendar, _from=since, to=until, symbol=symbols[0], international=False)
        except finnhub.exceptions.FinnhubAPIException:
            return None

    out = {}
    for symbol in symbols:
        try:
            out[symbol] = await asyncio.to_thread(finnhub_client.earnings_calendar, _from=since, to=until, symbol=symbol, international=False)
        except finnhub.exceptions.FinnhubAPIException:
            out[symbol] = None
    return out

async def get_company_news(name: str, since: str, until: str) -> dict | None:
    symbols = await _resolve_symbols(name)
    if not symbols:
        return None

    filters = ["earnings", "guidance", "forecast", "revenue", "margin", "lawsuit", "regulation", "acquisition", "partnership", "ai", "product launch"]

    if len(symbols) == 1:
        try:
            response = await asyncio.to_thread(finnhub_client.company_news, _from=since, to=until, symbol=symbols[0])
            out = []
            for new in response:
                text = (new.get("headline", "") + " " + new.get("summary", "")).lower()
                if any(x in text for x in filters):
                    out.append(f'Date: {datetime.fromtimestamp(new.get("datetime"))} | Header: {new.get("headline")} | Content: {new.get("summary")}')
            if len(out) <= 5:
                return out
            else:
                return out[:4]
        except finnhub.exceptions.FinnhubAPIException:
            return None

    out = {}
    for symbol in symbols:
        try:
            response = await asyncio.to_thread(finnhub_client.company_news, _from=since, to=until, symbol=symbol)
            symbol_news = []
            for new in response:
                text = (new.get("headline", "") + " " + new.get("summary", "")).lower()
                if any(x in text for x in filters):
                    symbol_news.append(f'Date: {datetime.fromtimestamp(new.get("datetime"))} | Header: {new.get("headline")} | Content: {new.get("summary")}')
            
            if len(symbol_news) <= 3:
                out[symbol] = symbol_news
            else:
                out[symbol] = symbol_news[:2]
        except finnhub.exceptions.FinnhubAPIException:
            out[symbol] = None
    return out

async def get_company_profile(name: str, since: str, until: str) -> dict | None:
    symbols = await _resolve_symbols(name)
    if not symbols:
        return None

    if len(symbols) == 1:
        try:
            return await asyncio.to_thread(finnhub_client.company_profile2, symbol=symbols[0])
        except finnhub.exceptions.FinnhubAPIException:
            return None

    out = {}
    for symbol in symbols:
        try:
            out[symbol] = await asyncio.to_thread(finnhub_client.company_profile2, symbol=symbol)
        except finnhub.exceptions.FinnhubAPIException:
            out[symbol] = None
    return out

# response = asyncio.run(get_company_news("kaspi", "2026-01-30", "2026-04-30"))
# print(response)