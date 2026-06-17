import logging
import os

from celery import Celery

logger = logging.getLogger(__name__)

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

app = Celery("otel_celery_example", broker=broker_url, backend=result_backend)


@app.task
def add(x, y):
    logger.info("Adding %s and %s", x, y)
    return x + y
