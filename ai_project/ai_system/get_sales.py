# Finnhub, Alpha Vantage, Financial Modeling Prep (FMP), Alpaca Markets (Data API), yfinance (Python-библиотека, не полноценный API), StockData.org, Polygon.io (5RPM), Marketstack (100RPM)

from config import settings
import finnhub
import time

# Вставь сюда свой API-ключ (получи бесплатно на https://finnhub.io/register)
API_KEY = settings.finnhub_token

# Создаём клиент
client = finnhub.Client(api_key=API_KEY)

# # Получаем котировку акции (quote)
# symbol = "TSLA"          # Можно менять: TSLA, MSFT, NVDA, SBER.ME и т.д.
# quote = client.quote(symbol)

# print(f"Данные по {symbol}:")
# print(f"Текущая цена (c)     : {quote['c']}")
# print(f"Изменение (d)       : {quote['d']}")
# print(f"Процент изменения (dp): {quote['dp']}%")
# print(f"Открытие (o)        : {quote['o']}")
# print(f"Максимум (h)        : {quote['h']}")
# print(f"Минимум (l)         : {quote['l']}")
# print(f"Предыдущее закрытие (pc): {quote['pc']}")

response = client.company_news('MSFT', _from="2026-04-24", to="2026-04-24")
print(response)