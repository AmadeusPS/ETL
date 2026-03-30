"""
Azure Functions – Timer Trigger for scheduled price scraping.
Replaces AWS EventBridge cron + Lambda.

Triggers twice daily (08:00 and 20:00 Lisbon time = 07:00 and 19:00 UTC)
and enqueues the Celery fan-out task via Redis.

Deploy this function to the Azure Function App created by Terraform.
"""
import os
import json
import logging
import azure.functions as func

app = func.FunctionApp()


def _enqueue_scrape(timer_name: str) -> None:
    """Push a Celery task message onto the Redis broker queue."""
    import redis

    redis_url = os.environ["REDIS_URL"]
    r = redis.from_url(redis_url, decode_responses=False)

    # Celery task message format (protocol v2)
    task_message = {
        "id": f"azure-trigger-{timer_name}",
        "task": "app.workers.tasks.scrape_all_active_urls",
        "args": [],
        "kwargs": {},
        "retries": 0,
        "eta": None,
        "expires": None,
        "utc": True,
        "callbacks": None,
        "errbacks": None,
        "timelimit": [None, None],
        "taskset": None,
        "chord": None,
    }

    r.lpush("celery", json.dumps(task_message))
    logging.info("Enqueued scrape_all_active_urls via %s trigger", timer_name)


@app.timer_trigger(
    schedule="0 0 7 * * *",   # 07:00 UTC = 08:00 Lisbon (WEST)
    arg_name="morning_timer",
    run_on_startup=False,
)
def scrape_morning(morning_timer: func.TimerRequest) -> None:
    if morning_timer.past_due:
        logging.warning("Morning scrape trigger is past due")
    _enqueue_scrape("morning")


@app.timer_trigger(
    schedule="0 0 19 * * *",  # 19:00 UTC = 20:00 Lisbon (WEST)
    arg_name="evening_timer",
    run_on_startup=False,
)
def scrape_evening(evening_timer: func.TimerRequest) -> None:
    if evening_timer.past_due:
        logging.warning("Evening scrape trigger is past due")
    _enqueue_scrape("evening")
