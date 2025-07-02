# backend/api/routes/scraping.py
"""Scraping job management endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from core.database import get_db
from core.models import ScrapeJob, Store, CurrentOffer
from tasks.scraping_tasks import discover_stores_for_postal_code, scrape_store_offers, test_scraping_methods
from scrapers import ScrapingOrchestrator

router = APIRouter()

class PostalCodeRequest(BaseModel):
    postal_code: str
    force_refresh: bool = False

class ScrapingTestResponse(BaseModel):
    success: bool
    available_methods: List[str]
    test_results: dict
    total_available: int
    error: Optional[str] = None

@router.post("/test")
async def test_scrapers() -> ScrapingTestResponse:
    """Test all available scraping methods."""
    try:
        task = test_scraping_methods.delay()
        result = task.get(timeout=30)
        return ScrapingTestResponse(**result)
    except Exception as e:
        return ScrapingTestResponse(
            success=False,
            available_methods=[],
            test_results={},
            total_available=0,
            error=str(e)
        )

@router.post("/postal-code")
async def scrape_postal_code(request: PostalCodeRequest, db: Session = Depends(get_db)):
    """Start scraping for a postal code."""
    try:
        # Clean postal code
        postal_code = request.postal_code.replace(" ", "").upper()
        if len(postal_code) == 6:
            postal_code = postal_code[:3] + " " + postal_code[3:]
        
        # Check if we already have recent data (unless force refresh)
        if not request.force_refresh:
            existing_stores = db.query(Store).filter(Store.postal_code == postal_code).all()
            if existing_stores:
                return {
                    "message": f"Found {len(existing_stores)} existing stores for {postal_code}",
                    "postal_code": postal_code,
                    "stores_count": len(existing_stores),
                    "job_id": None,
                    "status": "existing_data"
                }
        
        # Start background scraping job
        task = discover_stores_for_postal_code.delay(postal_code)
        
        return {
            "message": f"Started scraping for postal code {postal_code}",
            "postal_code": postal_code,
            "job_id": task.id,
            "status": "started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs")
async def create_scrape_job(request: PostalCodeRequest, db: Session = Depends(get_db)):
    """Create a new scraping job (alias for postal-code endpoint)."""
    return await scrape_postal_code(request, db)

@router.get("/jobs/{job_id}")
async def get_scrape_job(job_id: str):
    """Get scraping job status."""
    try:
        from celery.result import AsyncResult
        task = AsyncResult(job_id)
        
        if task.state == 'PENDING':
            return {
                "job_id": job_id,
                "status": "pending",
                "message": "Job is waiting to be processed"
            }
        elif task.state == 'PROGRESS':
            return {
                "job_id": job_id,
                "status": "running",
                "progress": task.info,
                "message": "Job is currently running"
            }
        elif task.state == 'SUCCESS':
            return {
                "job_id": job_id,
                "status": "completed",
                "result": task.info,
                "message": "Job completed successfully"
            }
        else:
            return {
                "job_id": job_id,
                "status": "failed",
                "error": str(task.info),
                "message": "Job failed"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stores/{store_id}/scrape")
async def scrape_store(store_id: int, db: Session = Depends(get_db)):
    """Start scraping for a specific store."""
    try:
        # Verify store exists
        store = db.query(Store).filter(Store.store_id == store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Start background scraping job
        task = scrape_store_offers.delay(store_id)
        
        return {
            "message": f"Started scraping for store {store.name}",
            "store_id": store_id,
            "store_name": store.name,
            "job_id": task.id,
            "status": "started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stores/{store_id}/offers")
async def get_store_offers(store_id: int, db: Session = Depends(get_db)):
    """Get current offers for a store."""
    try:
        # Verify store exists
        store = db.query(Store).filter(Store.store_id == store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Get offers
        offers = db.query(CurrentOffer).filter(CurrentOffer.store_id == store_id).all()
        
        return {
            "store_id": store_id,
            "store_name": store.name,
            "offers_count": len(offers),
            "last_scraped": store.last_scraped.isoformat() if store.last_scraped else None,
            "offers": [
                {
                    "offer_id": offer.offer_id,
                    "product_name": offer.product_name,
                    "brand": offer.brand,
                    "category": offer.category,
                    "price": offer.price,
                    "original_price": offer.original_price,
                    "unit": offer.unit,
                    "discount_percentage": offer.discount_percentage,
                    "is_featured_deal": offer.is_featured_deal,
                    "start_date": offer.start_date.isoformat() if offer.start_date else None,
                    "end_date": offer.end_date.isoformat() if offer.end_date else None,
                    "description": offer.description,
                    "image_url": offer.image_url
                }
                for offer in offers
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/postal-codes/{postal_code}/stores")
async def get_postal_code_stores(postal_code: str, db: Session = Depends(get_db)):
    """Get all stores for a postal code."""
    try:
        # Clean postal code
        postal_code = postal_code.replace(" ", "").upper()
        if len(postal_code) == 6:
            postal_code = postal_code[:3] + " " + postal_code[3:]
        
        stores = db.query(Store).filter(Store.postal_code == postal_code).all()
        
        return {
            "postal_code": postal_code,
            "stores_count": len(stores),
            "stores": [
                {
                    "store_id": store.store_id,
                    "name": store.name,
                    "chain": store.chain,
                    "address": store.address,
                    "phone": store.phone,
                    "website": store.website,
                    "last_scraped": store.last_scraped.isoformat() if store.last_scraped else None,
                    "scrape_config": store.scrape_config
                }
                for store in stores
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
