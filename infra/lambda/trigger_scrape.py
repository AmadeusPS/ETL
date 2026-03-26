"""
Lambda function invoked by EventBridge (2x/day).
Pushes a Celery task message directly to Redis so the ECS worker picks it up.
Deploy: zip this file + celery/kombu deps, upload to S3, reference in Terraform.
"""
import json
import os
import uuid
import time

import redis


REDIS_URL = os.environ["REDIS_URL"]
CELERY_QUEUE = "celery"


def handler(event, context):
    r = redis.from_url(REDIS_URL, decode_responses=True)

    task_id = str(uuid.uuid4())
    message = {
        "id": task_id,
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

    r.lpush(CELERY_QUEUE, json.dumps(message))
    print(f"Enqueued scrape task {task_id}")
    return {"statusCode": 200, "body": json.dumps({"task_id": task_id})}
