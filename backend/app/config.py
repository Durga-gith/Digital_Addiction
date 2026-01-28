import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 🔹 Explicitly load .env from PROJECT ROOT
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)


class Settings(BaseSettings):
    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    FRONTEND_URL: str
    ENVIRONMENT: str

    class Config:
        case_sensitive = True


settings = Settings()
