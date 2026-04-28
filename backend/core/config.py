from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn


class Settings(BaseSettings):
    DB_URL: PostgresDsn
    DB_ALTER_URL: PostgresDsn

    ALPACA_API_KEY: str
    ALPACA_SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()