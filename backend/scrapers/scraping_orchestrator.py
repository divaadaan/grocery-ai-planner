# backend/scrapers/scraping_orchestrator.py
"""Main orchestrator for coordinating scraping methods."""

from typing import List, Dict, Any, Optional
import logging
from core.config import get_scraping_config
from .base_scraper import BaseScraper, ScrapingResult, ScrapingMethod
from .flipp_scraper import FlippAPIScraper, FlippWebScraper
from .selenium_scraper import SeleniumScraper
from .pdf_scraper import PDFScraper
from .vision_scraper import VisionScraper

logger = logging.getLogger(__name__)

class ScrapingOrchestrator:
    """
    Orchestrates scraping using the fallback hierarchy:
    1. Flipp API (primary)
    2. Selenium web scraping 
    3. PDF OCR
    4. Vision AI
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = get_scraping_config()
        self.config = config
        self.scrapers = self._initialize_scrapers()
        
    def _initialize_scrapers(self) -> List[BaseScraper]:
        """Initialize scrapers in order of preference."""
        scrapers = []
        
        # Only add enabled scrapers
        if self.config.get('flipp_api', {}).get('enabled', True):
            scrapers.append(FlippAPIScraper(self.config.get('flipp_api', {})))
            
        if self.config.get('selenium', {}).get('enabled', True):
            scrapers.append(FlippWebScraper(self.config.get('selenium', {})))
            scrapers.append(SeleniumScraper(self.config.get('selenium', {})))
            
        if self.config.get('pdf_ocr', {}).get('enabled', False):
            scrapers.append(PDFScraper(self.config.get('pdf_ocr', {})))
            
        if self.config.get('vision_ai', {}).get('enabled', False):
            scrapers.append(VisionScraper(self.config.get('vision_ai', {})))
        
        # Filter to only available scrapers
        available_scrapers = [s for s in scrapers if s.is_available()]
        
        logger.info(f"Initialized {len(available_scrapers)} available scrapers: "
                   f"{[s.method.value for s in available_scrapers]}")
        
        return available_scrapers
    
    def scrape_postal_code(self, postal_code: str, max_attempts: int = None) -> ScrapingResult:
        """
        Scrape stores and offers for a postal code using fallback hierarchy.
        
        Args:
            postal_code: Canadian postal code
            max_attempts: Maximum number of scraping methods to try
            
        Returns:
            ScrapingResult from the first successful scraper
        """
        if max_attempts is None:
            max_attempts = len(self.scrapers)
        
        last_error = "No scrapers available"
        
        for i, scraper in enumerate(self.scrapers[:max_attempts]):
            logger.info(f"Attempting scraping with {scraper.method.value} for postal code {postal_code}")
            
            try:
                result = scraper.scrape_postal_code(postal_code)
                
                if result.success and (result.stores or result.offers):
                    logger.info(f"Successfully scraped with {scraper.method.value}: "
                               f"{len(result.stores)} stores, {len(result.offers)} offers")
                    return result
                else:
                    logger.warning(f"{scraper.method.value} returned no data: {result.error_message}")
                    last_error = result.error_message or "No data returned"
                    
            except Exception as e:
                logger.error(f"{scraper.method.value} failed with exception: {str(e)}")
                last_error = str(e)
                continue
        
        # All scrapers failed
        return ScrapingResult(
            success=False,
            method_used=ScrapingMethod.FLIPP_API,  # Default
            stores=[],
            offers=[],
            error_message=f"All {max_attempts} scraping methods failed. Last error: {last_error}"
        )
    
    def scrape_store_url(self, store_url: str, store_name: str = None, max_attempts: int = None) -> ScrapingResult:
        """
        Scrape a specific store URL using fallback hierarchy.
        
        Args:
            store_url: URL to scrape
            store_name: Optional store name for context
            max_attempts: Maximum number of scraping methods to try
            
        Returns:
            ScrapingResult from the first successful scraper
        """
        if max_attempts is None:
            max_attempts = len(self.scrapers)
        
        last_error = "No scrapers available"
        
        # Skip Flipp API for direct store URLs (it needs postal code context)
        suitable_scrapers = [s for s in self.scrapers if s.method != ScrapingMethod.FLIPP_API]
        
        for scraper in suitable_scrapers[:max_attempts]:
            logger.info(f"Attempting scraping {store_url} with {scraper.method.value}")
            
            try:
                result = scraper.scrape_store(store_url, store_name)
                
                if result.success and result.offers:
                    logger.info(f"Successfully scraped {store_url} with {scraper.method.value}: "
                               f"{len(result.offers)} offers")
                    return result
                else:
                    logger.warning(f"{scraper.method.value} returned no data: {result.error_message}")
                    last_error = result.error_message or "No data returned"
                    
            except Exception as e:
                logger.error(f"{scraper.method.value} failed with exception: {str(e)}")
                last_error = str(e)
                continue
        
        # All scrapers failed
        return ScrapingResult(
            success=False,
            method_used=ScrapingMethod.SELENIUM,  # Default for store URLs
            stores=[],
            offers=[],
            error_message=f"All suitable scraping methods failed for {store_url}. Last error: {last_error}"
        )
    
    def get_available_methods(self) -> List[ScrapingMethod]:
        """Get list of available scraping methods."""
        return [scraper.method for scraper in self.scrapers]
    
    def test_scrapers(self) -> Dict[ScrapingMethod, bool]:
        """Test availability of all scrapers."""
        results = {}
        for scraper in self.scrapers:
            try:
                results[scraper.method] = scraper.is_available()
            except Exception as e:
                logger.error(f"Error testing {scraper.method.value}: {str(e)}")
                results[scraper.method] = False
        return results
    
    def force_method(self, method: ScrapingMethod) -> Optional[BaseScraper]:
        """Get a specific scraper by method."""
        for scraper in self.scrapers:
            if scraper.method == method:
                return scraper
        return None
