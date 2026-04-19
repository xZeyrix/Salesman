from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn


class Settings(BaseSettings):
    DB_URL: PostgresDsn
    DB_ALTER_URL: PostgresDsn
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()