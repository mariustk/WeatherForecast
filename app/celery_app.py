from celery import Celery
import os

BROKER  = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

# Celery app using docker
celery_app = Celery(
    "heavy_lifting_service",
    broker=BROKER,
    backend=BACKEND,
)

#Import submodules
celery_app.autodiscover_tasks(["app.celery_tasks"])

# Print all autodiscovered tasks:
