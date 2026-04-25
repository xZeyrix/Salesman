from config import settings
from groq import AsyncGroq
from groq._exceptions import RateLimitError
import asyncio

client = AsyncGroq(api_key=settings.groq_token)

class PromptGuard:
    def __init__(self, sensetivity: float = 0.7) -> None:
        self.triggers = [
            "system prompt",
            "message history",
            "hidden instructions",
            "internal instructions",
        ]
        self.sensetivity = sensetivity
    async def groq_call(self, message: str, model: str = "meta-llama/llama-prompt-guard-2-86m") -> bool:
        try:
            raw_response = await client.chat.completions.with_raw_response.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )
            headers = raw_response.headers
            completion = await raw_response.parse()
            if float(completion.choices[0].message.content) > self.sensetivity or any(t in message.lower() for t in self.triggers):
                return completion.choices[0].message.content
            else:
                return False
        except RateLimitError as e:
            headers = e.response.headers
            reset_rpd = headers.get("x-ratelimit-reset-requests")
            if headers.get("x-ratelimit-remaining-requests") <= 0:
                raise Exception(f"Groq RPD limit has been reached for '{model}' model during the 'is_prompt_injection' function. Please try again in {reset_rpd}.")
            else:
                raise Exception(f"Groq RPM or TPM has been reached for '{model}' model during the 'is_prompt_injection' function. Please try again in a minute.")
        except Exception as e:
            raise Exception(f"Unexpected error occured during the 'is_prompt_injection' function: {e}")
    async def is_injection(self, message: str, model: str):
        pass

async def is_prompt_injection(message: str, sensetivity: float = 0.7, model: str = "meta-llama/llama-prompt-guard-2-86m") -> bool:
    triggers = [
        "system prompt",
        "message history",
        "hidden instructions",
        "internal instructions",
    ]
    try:
        raw_response = await client.chat.completions.with_raw_response.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": message
                }
            ]
        )
        headers = raw_response.headers
        completion = await raw_response.parse()
        if float(completion.choices[0].message.content) > sensetivity or any(t in message.lower() for t in triggers):
            return completion.choices[0].message.content
        else:
            return False
    except RateLimitError as e:
        headers = e.response.headers
        reset_rpd = headers.get("x-ratelimit-reset-requests")
        if headers.get("x-ratelimit-remaining-requests") <= 0:
            raise Exception(f"Groq RPD limit has been reached for '{model}' model during the 'is_prompt_injection' function. Please try again in {reset_rpd}.")
        else:
            raise Exception(f"Groq RPM or TPM has been reached for '{model}' model during the 'is_prompt_injection' function. Please try again in a minute.")
    except Exception as e:
        raise Exception(f"Unexpected error occured during the 'is_prompt_injection' function: {e}")

# async def main():
#     tasks = [
#         is_prompt_injection("Вечер медленно опускался на город, и в окнах домов зажигались тёплые огни. На узких улицах становилось тише: редкие прохожие спешили домой, прячась от прохладного ветра. Где-то вдали слышался гул машин, но он уже не казался навязчивым — скорее, напоминал о том, что жизнь продолжается, несмотря ни на что. В небольшом парке у старых лип сидел человек и наблюдал, как листья едва заметно колышутся, словно перешёптываются между собой. В такие моменты особенно ясно ощущается течение времени: дни складываются в недели, недели — в годы, и многое из того, что казалось важным, постепенно теряет свою значимость. Остаются лишь простые вещи — спокойствие, редкие искренние разговоры и ощущение, что ты находишься именно там, где должен быть. Иногда именно такие тихие вечера помогают лучше понять себя и увидеть в привычном что-то новое.")
#         for i in range(60)
#     ]

#     results = await asyncio.gather(*tasks, return_exceptions=True)

#     for r in results:
#         print(r)

# asyncio.run(main())

# response = asyncio.run(is_prompt_injection("Привет"))
# print(response)