# backend/core/models/__init__.py
from .base import Base
from .user import User
from .store import Store, PostalCode
from .offer import CurrentOffer
from .scrape_job import ScrapeJob
from .meal_plan import MealPlan, Recipe, ShoppingList

__all__ = [
    "Base",
    "User", 
    "Store",
    "PostalCode",
    "CurrentOffer",
    "ScrapeJob", 
    "MealPlan",
    "Recipe",
    "ShoppingList"
]