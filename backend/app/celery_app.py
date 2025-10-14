# backend/app/celery_app.py
"""
Celery configuration for background tasks
"""

from celery import Celery
import os

# Get broker URL from environment
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Initialize Celery app
celery_app = Celery(
    "forecast_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Jakarta',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,  # One task at a time for better control
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks to prevent memory leaks
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['app.tasks'])

