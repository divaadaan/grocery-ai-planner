# backend/scrapers/base_scraper.py
"""Base scraper class and common data structures."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ScrapingMethod(Enum):
    """Available scraping methods in order of preference."""
    FLIPP_API = "flipp_api"
    SELENIUM = "selenium"
    PDF_OCR = "pdf_ocr"
    VISION_AI = "vision_ai"

@dataclass
class OfferData:
    """Standardized offer data structure."""
    product_name: str
    price: float
    store_name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    unit: Optional[str] = None
    original_price: Optional[float] = None
    discount_percentage: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_featured_deal: bool = False
    description: Optional[str] = None
    image_url: Optional[str] = None
    
@dataclass
class StoreData:
    """Standardized store data structure."""
    name: str
    chain: str
    address: str
    postal_code: str
    phone: Optional[str] = None
    website: Optional[str] = None
    flyer_url: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None

@dataclass 
class ScrapingResult:
    """Result from a scraping operation."""
    success: bool
    method_used: ScrapingMethod
    stores: List[StoreData]
    offers: List[OfferData]
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

class BaseScraper(ABC):
    """Base class for all scrapers."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def scrape_postal_code(self, postal_code: str) -> ScrapingResult:
        """
        Scrape stores and offers for a given postal code.
        
        Args:
            postal_code: Canadian postal code (e.g., "M5V 3A8")
            
        Returns:
            ScrapingResult with stores and offers found
        """
        pass
    
    @abstractmethod
    def scrape_store(self, store_url: str, store_name: str = None) -> ScrapingResult:
        """
        Scrape offers from a specific store.
        
        Args:
            store_url: URL to scrape
            store_name: Optional store name for context
            
        Returns:
            ScrapingResult with offers found
        """
        pass
    
    @property
    @abstractmethod
    def method(self) -> ScrapingMethod:
        """Return the scraping method this scraper implements."""
        pass
    
    def is_available(self) -> bool:
        """
        Check if this scraper is available and properly configured.
        
        Returns:
            True if scraper can be used, False otherwise
        """
        return True
    
    def clean_postal_code(self, postal_code: str) -> str:
        """Standardize postal code format."""
        # Remove spaces and convert to uppercase
        cleaned = postal_code.replace(" ", "").upper()
        
        # Add space in correct position if not present
        if len(cleaned) == 6:
            cleaned = cleaned[:3] + " " + cleaned[3:]
            
        return cleaned
    
    def normalize_price(self, price_str: str) -> float:
        """Extract numeric price from string."""
        if not price_str:
            return 0.0
            
        # Remove currency symbols, spaces, and other non-numeric chars except decimal
        import re
        price_str = re.sub(r'[^\d.,]', '', str(price_str))
        
        # Handle different decimal separators
        if ',' in price_str and '.' in price_str:
            # Format like "1,234.56" - remove commas
            price_str = price_str.replace(',', '')
        elif ',' in price_str:
            # Could be European format "1,56" or thousands "1,234"
            parts = price_str.split(',')
            if len(parts[-1]) <= 2:  # Likely decimal
                price_str = price_str.replace(',', '.')
            else:  # Likely thousands separator
                price_str = price_str.replace(',', '')
        
        try:
            return float(price_str)
        except (ValueError, TypeError):
            self.logger.warning(f"Could not parse price: {price_str}")
            return 0.0
