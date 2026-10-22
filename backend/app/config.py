import os

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field

    class Settings(BaseSettings):
        APP_NAME: str = "Household Finance Tracker"
        DATABASE_URL: str = Field(
            default="postgresql+asyncpg://rentapp:rentapp_secure_password@localhost:5432/household_tracker"
        )
        DEBUG: bool = False

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            extra = "ignore"

    settings = Settings()
except ImportError:
    class SettingsFallback:
        APP_NAME: str = os.environ.get("APP_NAME", "Household Finance Tracker")
        DATABASE_URL: str = os.environ.get(
            "DATABASE_URL",
            "postgresql+asyncpg://rentapp:rentapp_secure_password@localhost:5432/household_tracker"
        )
        DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"

    settings = SettingsFallback()
