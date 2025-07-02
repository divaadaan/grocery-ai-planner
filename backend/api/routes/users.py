# backend/api/routes/users.py
"""User management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from core.database import get_db
from core.models import User

router = APIRouter()


class UserCreate(BaseModel):
    email: str
    postal_code: str
    budget: float
    household_size: int = 1
    dietary_restrictions: List[str] = []
    food_preferences: dict = {}


class UserResponse(BaseModel):
    user_id: int
    email: str
    postal_code: str
    budget: float
    household_size: int
    
    class Config:
        from_attributes = True


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user