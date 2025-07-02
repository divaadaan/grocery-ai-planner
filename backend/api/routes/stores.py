# backend/api/routes/stores.py
"""Store discovery and management endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/discover/{postal_code}")
async def discover_stores(postal_code: str):
    """Discover stores for a postal code."""
    return {"message": f"Store discovery for {postal_code} - to be implemented"}


@router.get("/{postal_code}")
async def get_stores(postal_code: str):
    """Get stores for a postal code."""
    return {"message": f"Get stores for {postal_code} - to be implemented"}