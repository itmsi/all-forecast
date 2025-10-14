# backend/app/tasks/__init__.py
"""
Celery tasks
"""

from .forecast_task import run_forecast_task, train_model_task

__all__ = ['run_forecast_task', 'train_model_task']

