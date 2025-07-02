# backend/api/routes/meal_plans.py
"""Meal planning endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/generate")
async def generate_meal_plan():
    """Generate AI meal plan."""
    return {"message": "Meal plan generation - to be implemented"}


@router.get("/{plan_id}")
async def get_meal_plan(plan_id: int):
    """Get meal plan by ID."""
    return {"message": f"Get meal plan {plan_id} - to be implemented"}