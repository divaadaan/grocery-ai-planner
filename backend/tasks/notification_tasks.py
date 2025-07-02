# backend/tasks/notification_tasks.py
"""Email notification tasks."""

import logging
from celery import current_task
from worker import celery_app
from core.config import get_settings

logger = logging.getLogger(__name__)


@celery_app.task
def send_scraping_complete_email(user_email: str, postal_code: str, stores_found: int):
    """
    Send email notification when scraping is complete.
    
    Args:
        user_email: User's email address
        postal_code: The postal code that was scraped
        stores_found: Number of stores found
    """
    logger.info(f"Sending scraping complete email to {user_email}")
    
    settings = get_settings()
    
    # TODO: Implement actual email sending
    # This will use FastAPI-Mail or similar
    
    if not settings.mail_username:
        logger.warning("Email not configured, skipping notification")
        return {"status": "skipped", "reason": "email_not_configured"}
    
    try:
        # Simulate email sending
        import time
        time.sleep(1)
        
        logger.info(f"Scraping complete email sent to {user_email}")
        return {
            "status": "sent",
            "recipient": user_email,
            "subject": f"Grocery deals ready for {postal_code}",
            "stores_found": stores_found
        }
        
    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {str(e)}")
        raise


@celery_app.task
def send_meal_plan_ready_email(user_email: str, plan_id: int, total_cost: float, savings: float):
    """
    Send email notification when meal plan is ready.
    
    Args:
        user_email: User's email address
        plan_id: Generated meal plan ID
        total_cost: Total cost of the meal plan
        savings: Amount saved compared to regular prices
    """
    logger.info(f"Sending meal plan ready email to {user_email}")
    
    settings = get_settings()
    
    if not settings.mail_username:
        logger.warning("Email not configured, skipping notification")
        return {"status": "skipped", "reason": "email_not_configured"}
    
    try:
        # Simulate email sending
        import time
        time.sleep(1)
        
        logger.info(f"Meal plan ready email sent to {user_email}")
        return {
            "status": "sent",
            "recipient": user_email,
            "subject": "Your AI meal plan is ready!",
            "plan_id": plan_id,
            "total_cost": total_cost,
            "savings": savings
        }
        
    except Exception as e:
        logger.error(f"Failed to send meal plan email to {user_email}: {str(e)}")
        raise