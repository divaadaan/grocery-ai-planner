# backend/core/models/user.py
from sqlalchemy import Column, Integer, String, Float, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    postal_code = Column(String(10), nullable=False, index=True)
    
    # User preferences
    budget = Column(Float, nullable=False)  # Weekly budget
    household_size = Column(Integer, nullable=False, default=1)
    
    # Dietary restrictions and preferences as JSON
    dietary_restrictions = Column(JSON, default=list)  # ["vegetarian", "gluten-free", etc.]
    food_preferences = Column(JSON, default=dict)     # {"likes": [], "dislikes": [], "allergies": []}
    
    # Settings
    preferred_stores = Column(JSON, default=list)     # Store IDs in order of preference
    max_shopping_trips = Column(Integer, default=2)   # Max stores to visit per week
    is_active = Column(Boolean, default=True)
    
    # Relationships
    meal_plans = relationship("MealPlan", back_populates="user")
    
    def __repr__(self):
        return f"<User(email='{self.email}', postal_code='{self.postal_code}')>"