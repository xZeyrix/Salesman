from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, PostgresDsn
from ai_project.ai_system.prompts import router_prompt, salesman_prompt, history_prompt


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    bot_token: str
    groq_token: str
    finnhub_token: str

    DB_URL: PostgresDsn
    DB_ALTER_URL: PostgresDsn

    ALPACA_API_KEY: str
    ALPACA_SECRET_KEY: str

    # ВАЖНО если потерять вернет кей то придется дропнуть таблицу с ключами кошельков и заново генерировать новый шифр 
    # и всем придется регать кошельки вновь
    FERNET_KEY: str


class Prompts(BaseModel):
    router: str = router_prompt
    salesman: str = salesman_prompt
    history: str = history_prompt


settings = Settings()
prompts = Prompts()