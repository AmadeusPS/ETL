from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "PriceWatch.pt"
    environment: str = "development"
    debug: bool = False

    # Database (Azure Database for PostgreSQL Flexible Server)
    database_url: str = "postgresql://pricewatch:secret@localhost:5432/pricewatch"

    # Azure AD B2C
    b2c_tenant_name: str = ""        # e.g. "pricewatchusers" (without .onmicrosoft.com)
    b2c_client_id: str = ""          # Frontend app registration client ID
    b2c_policy_name: str = "B2C_1_signupsignin"

    # Redis (Azure Cache for Redis – use rediss:// with SSL in production)
    redis_url: str = "redis://localhost:6379/0"

    # Anthropic / Claude
    anthropic_api_key: str = ""

    # Scraping
    scrape_concurrency: int = 5
    scrape_delay_seconds: float = 1.0

    # Plans
    plan_basic_max_stores: int = 3
    plan_basic_max_products: int = 50
    plan_pro_max_stores: int = 10
    plan_pro_max_products: int = 500
    plan_enterprise_max_stores: int = 100
    plan_enterprise_max_products: int = 10000


@lru_cache
def get_settings() -> Settings:
    return Settings()
