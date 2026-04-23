# import hmac
# import hashlib
# import time
# import json
# import httpx
# from urllib.parse import urlencode

# class TradernetAI:
#     BASE_URL = "https://tradernet.kz"

#     @staticmethod
#     def _generate_signature(cmd: str, params: dict, nonce: int, secret_key: str) -> str:
#         # Важно: params в строке подписи должен быть в JSON формате
#         params_json = json.dumps(params)
#         p_string = f"cmd={cmd}&nonce={nonce}&params={params_json}"
        
#         return hmac.new(
#             secret_key.encode('utf-8'),
#             p_string.encode('utf-8'),
#             hashlib.sha256
#         ).hexdigest()

#     @classmethod
#     async def fetch_user_data(cls, api_key: str, secret_key: str, cmd: str = "getPositionJson", params: dict = None):
#         """
#         Универсальный метод: передаешь ключи юзера -> получаешь данные
#         """
#         if params is None:
#             params = {}
            
#         nonce = int(time.time() * 1000)
#         signature = cls._generate_signature(cmd, params, nonce, secret_key)
        
#         # Формируем тело запроса
#         payload = {
#             'cmd': cmd,
#             'params': params, # httpx сам конвертирует в JSON если слать через json=
#             'nonce': nonce,
#             'apiKey': api_key,
#             'sig': signature
#         }

#         async with httpx.AsyncClient() as client:
#             try:
#                 # Отправляем как JSON, Tradernet API это поддерживает
#                 response = await client.post(cls.BASE_URL, json=payload, timeout=10.0)
#                 return response.json()
#             except Exception as e:
#                 return {"status": "error", "message": str(e)}

#     # Удобные обертки
#     @classmethod
#     async def get_portfolio(cls, api_key: str, secret_key: str):
#         return await cls.fetch_user_data(api_key, secret_key, "getPositionJson")

#     @classmethod
#     async def get_balance(cls, api_key: str, secret_key: str):
#         return await cls.fetch_user_data(api_key, secret_key, "getAccountSummary")
