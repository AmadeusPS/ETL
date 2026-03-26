from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "PriceWatch.pt"
    environment: str = "development"
    debug: bool = False

    # Database (Amazon RDS PostgreSQL)
    database_url: str = "postgresql://pricewatch:secret@localhost:5432/pricewatch"

    # AWS Cognito
    aws_region: str = "eu-west-1"
    cognito_user_pool_id: str = ""
    cognito_client_id: str = ""
    cognito_client_secret: str = ""

    # Redis (ElastiCache) – Celery broker
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
