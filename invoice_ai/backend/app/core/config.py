from typing import ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg2://invoiceai:invoiceai@localhost:5432/invoiceai"

    OVERAGE_UNIT_PRICE_MICROS: dict[str, int] = {
        "gemini": 1000,
        "claude": 1500,
    }
    OVERAGE_CURRENCY: str = "EUR"

    # Not an env setting (constant), so keep as ClassVar
    PROVIDER_PRIORITY: ClassVar[list[str]] = ["gemini", "claude"]


settings = Settings()
