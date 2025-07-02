# backend/core/models/meal_plan.py
from sqlalchemy import Column, Integer, String, Float, Text, Date, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class MealPlan(Base, TimestampMixin):
    __tablename__ = "meal_plans"
    
    plan_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    
    # Plan details
    week_start = Column(Date, nullable=False)
    week_end = Column(Date, nullable=False)
    
    # Financial summary
    total_cost = Column(Float, nullable=False)
    target_budget = Column(Float, nullable=False)
    savings_amount = Column(Float, default=0)  # Amount saved vs regular prices
    
    # Plan data (JSON storage for flexibility)
    recipes = Column(JSON, nullable=False)  # Full recipe data
    shopping_list = Column(JSON, nullable=False)  # Consolidated shopping list
    store_breakdown = Column(JSON, default=dict)  # Shopping list by store
    
    # Nutritional summary
    nutrition_summary = Column(JSON, default=dict)  # Daily averages, weekly totals
    
    # Status
    is_active = Column(Boolean, default=True)
    user_feedback = Column(Text)  # User notes/feedback on the plan
    
    # Relationships
    user = relationship("User", back_populates="meal_plans")
    
    def __repr__(self):
        return f"<MealPlan(user_id={self.user_id}, week_start='{self.week_start}', cost=${self.total_cost:.2f})>"

class Recipe(Base, TimestampMixin):
    __tablename__ = "recipes"
    
    recipe_id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("meal_plans.plan_id"))
    
    # Recipe details
    name = Column(String(255), nullable=False)
    meal_type = Column(String(20), nullable=False)  # "breakfast", "lunch", "dinner", "snack"
    servings = Column(Integer, nullable=False)
    prep_time = Column(Integer)  # minutes
    cook_time = Column(Integer)  # minutes
    
    # Recipe content
    ingredients = Column(JSON, nullable=False)  # [{"name": "...", "amount": "...", "unit": "..."}]
    instructions = Column(JSON, nullable=False)  # ["step 1", "step 2", ...]
    
    # Nutritional info
    nutrition = Column(JSON, default=dict)  # Per serving nutrition facts
    
    # Cost breakdown
    estimated_cost = Column(Float, nullable=False)
    cost_per_serving = Column(Float, nullable=False)
    
    # Metadata
    difficulty_level = Column(String(20), default="medium")  # "easy", "medium", "hard"
    cuisine_type = Column(String(50))
    dietary_tags = Column(JSON, default=list)  # ["vegetarian", "gluten-free", etc.]
    
    def __repr__(self):
        return f"<Recipe(name='{self.name}', meal_type='{self.meal_type}')>"

class ShoppingList(Base, TimestampMixin):
    __tablename__ = "shopping_lists"
    
    list_id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("meal_plans.plan_id"))
    
    # Shopping optimization
    total_items = Column(Integer, nullable=False)
    total_cost = Column(Float, nullable=False)
    stores_count = Column(Integer, nullable=False)
    
    # List data
    items_by_store = Column(JSON, nullable=False)  # {"store_id": [items...]}
    consolidated_items = Column(JSON, nullable=False)  # All items with quantities
    
    # Shopping route optimization
    suggested_route = Column(JSON, default=list)  # Store visit order
    estimated_shopping_time = Column(Integer)  # minutes
    
    def __repr__(self):
        return f"<ShoppingList(plan_id={self.plan_id}, items={self.total_items}, cost=${self.total_cost:.2f})>"