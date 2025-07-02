# backend/tasks/scraping_tasks.py
"""Scraping-related background tasks."""

import logging
from datetime import datetime
from celery import current_task
from worker import celery_app
from core.database import SessionLocal
from core.models import ScrapeJob, ScrapeJobStatus, Store, CurrentOffer
from scrapers import ScrapingOrchestrator, ScrapingMethod

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def discover_stores_for_postal_code(self, postal_code: str):
    """
    Background task to discover stores for a postal code using new scraping framework.
    
    Args:
        postal_code: The postal code to search stores for
    """
    logger.info(f"Starting store discovery for postal code: {postal_code}")
    
    # Update job status
    db = SessionLocal()
    job = None
    try:
        # Create or update scrape job
        job = ScrapeJob(
            postal_code=postal_code,
            status=ScrapeJobStatus.RUNNING,
            job_type="store_discovery",
            started_at=datetime.utcnow()
        )
        db.add(job)
        db.commit()
        
        # Update task state
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Initializing scraping...'}
        )
        
        # Initialize scraping orchestrator
        orchestrator = ScrapingOrchestrator()
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 25, 'total': 100, 'status': 'Starting store discovery...'}
        )
        
        # Scrape using fallback hierarchy
        result = orchestrator.scrape_postal_code(postal_code)
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 75, 'total': 100, 'status': 'Processing results...'}
        )
        
        if result.success:
            # Save stores to database
            stores_added = 0
            offers_added = 0
            
            for store_data in result.stores:
                # Check if store already exists
                existing_store = db.query(Store).filter(
                    Store.name == store_data.name,
                    Store.postal_code == postal_code
                ).first()
                
                if not existing_store:
                    store = Store(
                        name=store_data.name,
                        chain=store_data.chain,
                        address=store_data.address,
                        postal_code=postal_code,
                        phone=store_data.phone,
                        website=store_data.website,
                        flyer_url=store_data.flyer_url,
                        latitude=store_data.latitude,
                        longitude=store_data.longitude,
                        last_scraped=datetime.utcnow(),
                        scrape_config={'source': result.method_used.value}
                    )
                    db.add(store)
                    stores_added += 1
            
            # Save offers to database
            for offer_data in result.offers:
                # Find the store for this offer
                store = db.query(Store).filter(
                    Store.name == offer_data.store_name,
                    Store.postal_code == postal_code
                ).first()
                
                if store:
                    # Remove existing offers for this store (to update with fresh data)
                    db.query(CurrentOffer).filter(
                        CurrentOffer.store_id == store.store_id
                    ).delete()
                    
                    offer = CurrentOffer(
                        store_id=store.store_id,
                        product_name=offer_data.product_name,
                        brand=offer_data.brand,
                        category=offer_data.category,
                        price=offer_data.price,
                        original_price=offer_data.original_price,
                        unit=offer_data.unit,
                        is_featured_deal=offer_data.is_featured_deal,
                        discount_percentage=offer_data.discount_percentage,
                        start_date=offer_data.start_date,
                        end_date=offer_data.end_date,
                        description=offer_data.description,
                        image_url=offer_data.image_url
                    )
                    db.add(offer)
                    offers_added += 1
            
            db.commit()
            
            # Mark job as completed
            job.status = ScrapeJobStatus.COMPLETED
            job.stores_found = stores_added
            job.offers_scraped = offers_added
            job.completed_at = datetime.utcnow()
            job.config = {
                'method_used': result.method_used.value,
                'metadata': result.metadata
            }
            db.commit()
            
            logger.info(f"Store discovery completed for {postal_code}: "
                       f"{stores_added} stores, {offers_added} offers using {result.method_used.value}")
            
            return {
                'current': 100, 
                'total': 100, 
                'status': f'Completed: {stores_added} stores, {offers_added} offers',
                'method_used': result.method_used.value
            }
        else:
            # Mark job as failed
            job.status = ScrapeJobStatus.FAILED
            job.error_log = [result.error_message]
            job.completed_at = datetime.utcnow()
            db.commit()
            
            logger.error(f"Store discovery failed for {postal_code}: {result.error_message}")
            raise Exception(result.error_message)
        
    except Exception as e:
        logger.error(f"Store discovery failed for {postal_code}: {str(e)}")
        
        # Mark job as failed
        if job:
            job.status = ScrapeJobStatus.FAILED
            job.error_log = [str(e)]
            job.completed_at = datetime.utcnow()
            db.commit()
        
        raise
    finally:
        db.close()


@celery_app.task
def test_scraping_methods():
    """
    Background task to test all available scraping methods.
    
    Returns:
        Dict with test results for each scraping method
    """
    logger.info("Testing scraping methods...")
    
    try:
        orchestrator = ScrapingOrchestrator()
        results = orchestrator.test_scrapers()
        
        # Convert enum keys to strings for JSON serialization
        string_results = {method.value: available for method, available in results.items()}
        
        logger.info(f"Scraping method test results: {string_results}")
        return {
            'success': True,
            'available_methods': list(string_results.keys()),
            'test_results': string_results,
            'total_available': sum(string_results.values())
        }
        
    except Exception as e:
        logger.error(f"Scraping method testing failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'available_methods': [],
            'test_results': {},
            'total_available': 0
        }


@celery_app.task(bind=True)
def scrape_store_offers(self, store_id: int):
    """
    Background task to scrape offers from a specific store using new framework.
    
    Args:
        store_id: The store ID to scrape offers from
    """
    logger.info(f"Starting offer scraping for store ID: {store_id}")
    
    db = SessionLocal()
    try:
        # Get store information
        store = db.query(Store).filter(Store.store_id == store_id).first()
        if not store:
            raise ValueError(f"Store not found: {store_id}")
        
        # Update task state
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': f'Starting scrape for {store.name}...'}
        )
        
        # Initialize scraping orchestrator
        orchestrator = ScrapingOrchestrator()
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 25, 'total': 100, 'status': f'Scraping {store.name}...'}
        )
        
        # Use store website or flyer URL
        target_url = store.flyer_url or store.website
        if not target_url:
            raise ValueError(f"No URL available for store {store.name}")
        
        # Scrape using fallback hierarchy
        result = orchestrator.scrape_store_url(target_url, store.name)
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 75, 'total': 100, 'status': 'Processing offers...'}
        )
        
        if result.success and result.offers:
            # Clear existing offers for this store
            db.query(CurrentOffer).filter(
                CurrentOffer.store_id == store_id
            ).delete()
            
            # Add new offers
            offers_added = 0
            for offer_data in result.offers:
                offer = CurrentOffer(
                    store_id=store_id,
                    product_name=offer_data.product_name,
                    brand=offer_data.brand,
                    category=offer_data.category,
                    price=offer_data.price,
                    original_price=offer_data.original_price,
                    unit=offer_data.unit,
                    is_featured_deal=offer_data.is_featured_deal,
                    discount_percentage=offer_data.discount_percentage,
                    start_date=offer_data.start_date,
                    end_date=offer_data.end_date,
                    description=offer_data.description,
                    image_url=offer_data.image_url
                )
                db.add(offer)
                offers_added += 1
            
            # Update store info
            store.last_scraped = datetime.utcnow()
            store.scrape_config = {
                'last_method': result.method_used.value,
                'last_success': True,
                'metadata': result.metadata
            }
            
            db.commit()
            
            logger.info(f"Offer scraping completed for {store.name}: "
                       f"{offers_added} offers using {result.method_used.value}")
            
            return {
                'current': 100, 
                'total': 100, 
                'status': f'Completed: {offers_added} offers for {store.name}',
                'offers_found': offers_added,
                'method_used': result.method_used.value
            }
        else:
            # Update store with failure info
            store.scrape_config = {
                'last_method': result.method_used.value if result else 'unknown',
                'last_success': False,
                'last_error': result.error_message if result else 'Unknown error'
            }
            db.commit()
            
            error_msg = result.error_message if result else "Unknown scraping error"
            logger.error(f"Offer scraping failed for {store.name}: {error_msg}")
            raise Exception(error_msg)
        
    except Exception as e:
        logger.error(f"Offer scraping failed for store {store_id}: {str(e)}")
        
        # Update store with error info if we have store object
        if 'store' in locals() and store:
            store.scrape_config = {
                'last_success': False,
                'last_error': str(e),
                'last_attempt': datetime.utcnow().isoformat()
            }
            db.commit()
        
        raise
    finally:
        db.close()