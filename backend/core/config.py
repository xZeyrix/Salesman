from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, BaseModel, PostgresDsn
from ai_project.ai_system.prompts import router_prompt, salesman_prompt, history_prompt

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env",
                                      env_file_encoding="utf-8")
    bot_token: str
    groq_token: str
    finnhub_token: str

    DB_URL: PostgresDsn
    DB_ALTER_URL: PostgresDsn

    ALPACA_API_KEY: str
    ALPACA_SECRET_KEY: str
    
class Prompts(BaseModel):
    router: str = router_prompt
    salesman: str = salesman_prompt
    history: str = history_prompt

settings = Settings()
prompts = Prompts()