# backend/worker.py
"""
Celery worker configuration for background tasks.
"""

import os
from celery import Celery
from core.config import get_celery_config

# Create Celery instance
celery_app = Celery("grocery_planner")

# Configure Celery
celery_app.config_from_object(get_celery_config())

# Auto-discover tasks
celery_app.autodiscover_tasks([
    'tasks.scraping_tasks',
    'tasks.meal_planning_tasks', 
    'tasks.notification_tasks'
])


if __name__ == '__main__':
    # For running celery worker
    celery_app.start()