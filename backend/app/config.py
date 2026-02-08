import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import validator

# 🔹 Explicitly load .env from PROJECT ROOT
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"  # Default for build/test, overridden in prod

    @validator("DATABASE_URL", pre=True)
    def fix_postgres_url(cls, v: str):
        if v and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    SECRET_KEY: str = "default_insecure_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    FRONTEND_URL: str = "*"
    ENVIRONMENT: str = "development"

    class Config:
        case_sensitive = True


settings = Settings()
