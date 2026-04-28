from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, BaseModel
from .prompts import router_prompt, salesman_prompt, history_prompt

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
    )

    bot_token: str
    groq_token: str
    finnhub_token: str

class Prompts(BaseModel):
    router: str = router_prompt
    salesman: str = salesman_prompt
    history: str = history_prompt

settings = Settings() # type:ignore
prompts = Prompts()