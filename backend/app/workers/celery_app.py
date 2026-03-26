"""
Celery application factory.
Broker: Redis (ElastiCache in production).
Beat schedule: 2x daily scrapes via EventBridge → Lambda → SQS (production)
               or Celery Beat (local/dev).
"""
from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "pricewatch",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Lisbon",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,  # fair dispatch for long-running scrape tasks
)

# ---------------------------------------------------------------------------
# Beat schedule (used in local dev; production uses EventBridge cron)
# ---------------------------------------------------------------------------
celery_app.conf.beat_schedule = {
    "scrape-all-morning": {
        "task": "app.workers.tasks.scrape_all_active_urls",
        "schedule": crontab(hour=8, minute=0),
    },
    "scrape-all-evening": {
        "task": "app.workers.tasks.scrape_all_active_urls",
        "schedule": crontab(hour=20, minute=0),
    },
}
