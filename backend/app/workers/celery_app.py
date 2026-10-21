import os
from celery import Celery
from app.core.config import settings

broker_url = os.environ.get("CELERY_BROKER_URL") or getattr(settings, "CELERY_BROKER_URL", "redis://localhost:6379/0")
backend_url = os.environ.get("CELERY_RESULT_BACKEND") or getattr(settings, "CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=backend_url,
    include=["app.workers.tasks"]
)
celery_app.conf.update(
    broker_connection_timeout=2.0,
    broker_connection_retry_on_startup=False,
    task_track_started=True,
)
