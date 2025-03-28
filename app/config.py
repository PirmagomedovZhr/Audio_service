import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str
    YANDEX_REDIRECT_URI: str

    JWT_SECRET: str
    JWT_ALGORITHM: str

    DEBUG: bool = False

    class Config:
        env_file = '.env'

settings = Settings()
