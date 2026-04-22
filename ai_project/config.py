from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
    )

    bot_token: str
    groq_token: str

settings = Settings() # type:ignore