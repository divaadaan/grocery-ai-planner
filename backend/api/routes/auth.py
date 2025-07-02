# backend/api/routes/auth.py
"""Authentication endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/register")
async def register():
    """User registration endpoint."""
    return {"message": "Registration endpoint - to be implemented"}


@router.post("/login")
async def login():
    """User login endpoint."""
    return {"message": "Login endpoint - to be implemented"}