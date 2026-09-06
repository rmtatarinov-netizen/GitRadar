from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GITHUB_TOKEN: str
    TELEGRAM_BOT_TOKEN: str
    DATABASE_URL: str
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
