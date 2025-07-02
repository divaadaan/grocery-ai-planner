# backend/scrapers/flipp_scraper.py
"""Flipp API and web scraping implementation."""

import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from .base_scraper import BaseScraper, ScrapingResult, ScrapingMethod, OfferData, StoreData

class FlippAPIScraper(BaseScraper):
    """Scraper using Flipp's undocumented API endpoints."""
    
    API_BASE = "https://backflipp.wishabi.com/flipp"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-CA,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        })
        
    @property
    def method(self) -> ScrapingMethod:
        return ScrapingMethod.FLIPP_API
    
    def scrape_postal_code(self, postal_code: str) -> ScrapingResult:
        """Scrape using Flipp API for a postal code."""
        postal_code = self.clean_postal_code(postal_code)
        
        try:
            # Search for all merchants in the area
            merchants_result = self._search_merchants(postal_code)
            
            if not merchants_result.success:
                return merchants_result
            
            stores = []
            all_offers = []
            
            # For each merchant, get their current offers
            for store_data in merchants_result.stores:
                self.logger.info(f"Fetching offers for {store_data.name}")
                
                offers_result = self._search_offers(postal_code, store_data.name)
                if offers_result.success:
                    stores.append(store_data)
                    all_offers.extend(offers_result.offers)
                    
                # Be respectful with rate limiting
                time.sleep(0.5)
            
            return ScrapingResult(
                success=True,
                method_used=self.method,
                stores=stores,
                offers=all_offers,
                metadata={
                    'postal_code': postal_code,
                    'merchants_found': len(stores),
                    'total_offers': len(all_offers)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Flipp API scraping failed: {str(e)}")
            return ScrapingResult(
                success=False,
                method_used=self.method,
                stores=[],
                offers=[],
                error_message=str(e)
            )
    
    def scrape_store(self, store_url: str, store_name: str = None) -> ScrapingResult:
        """Scrape specific store using Flipp API."""
        # For Flipp API, we need postal code context
        # This method is mainly for compatibility
        return ScrapingResult(
            success=False,
            method_used=self.method,
            stores=[],
            offers=[],
            error_message="Flipp API requires postal code context. Use scrape_postal_code instead."
        )
    
    def _search_merchants(self, postal_code: str) -> ScrapingResult:
        """Search for merchants in a postal code area."""
        try:
            # Try different search terms to find grocery stores
            grocery_terms = ["grocery", "supermarket", "No Frills", "Loblaws", "Metro", "Sobeys"]
            found_stores = set()
            
            for term in grocery_terms:
                url = f"{self.API_BASE}/items/search"
                params = {
                    'locale': 'en-ca',
                    'postal_code': postal_code,
                    'q': term
                }
                
                response = self.session.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract unique merchants from the response
                    if 'items' in data:
                        for item in data['items']:
                            merchant = item.get('merchant', {})
                            if merchant and merchant.get('name'):
                                found_stores.add((
                                    merchant['name'],
                                    merchant.get('id'),
                                    merchant.get('address', ''),
                                ))
                
                time.sleep(0.3)  # Rate limiting
            
            # Convert to StoreData objects
            stores = []
            for name, merchant_id, address in found_stores:
                if any(grocery_word in name.lower() for grocery_word in ['grocery', 'market', 'frills', 'loblaws', 'metro', 'sobeys', 'food']):
                    stores.append(StoreData(
                        name=name,
                        chain=self._extract_chain(name),
                        address=address,
                        postal_code=postal_code,
                        website="https://flipp.com"  # Reference back to Flipp
                    ))
            
            return ScrapingResult(
                success=True,
                method_used=self.method,
                stores=stores,
                offers=[],
                metadata={'search_terms': grocery_terms}
            )
            
        except Exception as e:
            self.logger.error(f"Merchant search failed: {str(e)}")
            return ScrapingResult(
                success=False,
                method_used=self.method,
                stores=[],
                offers=[],
                error_message=str(e)
            )
    
    def _search_offers(self, postal_code: str, merchant_name: str) -> ScrapingResult:
        """Search for offers from a specific merchant."""
        try:
            url = f"{self.API_BASE}/items/search"
            params = {
                'locale': 'en-ca',
                'postal_code': postal_code,
                'q': merchant_name
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return ScrapingResult(
                    success=False,
                    method_used=self.method,
                    stores=[],
                    offers=[],
                    error_message=f"API returned status {response.status_code}"
                )
            
            data = response.json()
            offers = []
            
            if 'items' in data:
                for item in data['items']:
                    offer = self._parse_offer_item(item, merchant_name)
                    if offer:
                        offers.append(offer)
            
            return ScrapingResult(
                success=True,
                method_used=self.method,
                stores=[],
                offers=offers,
                metadata={'merchant': merchant_name}
            )
            
        except Exception as e:
            self.logger.error(f"Offer search failed for {merchant_name}: {str(e)}")
            return ScrapingResult(
                success=False,
                method_used=self.method,
                stores=[],
                offers=[],
                error_message=str(e)
            )
    
    def _parse_offer_item(self, item: Dict[str, Any], store_name: str) -> Optional[OfferData]:
        """Parse a single offer item from Flipp API response."""
        try:
            name = item.get('name', '').strip()
            if not name:
                return None
            
            # Extract price information
            price = 0.0
            original_price = None
            
            if 'price' in item:
                price = self.normalize_price(item['price'])
            elif 'current_price' in item:
                price = self.normalize_price(item['current_price'])
                
            if 'original_price' in item:
                original_price = self.normalize_price(item['original_price'])
            
            # Calculate discount
            discount_percentage = None
            if original_price and original_price > price > 0:
                discount_percentage = int(((original_price - price) / original_price) * 100)
            
            # Extract dates
            start_date = None
            end_date = None
            
            if 'valid_from' in item:
                start_date = self._parse_date(item['valid_from'])
            if 'valid_to' in item:
                end_date = self._parse_date(item['valid_to'])
            
            return OfferData(
                product_name=name,
                price=price,
                store_name=store_name,
                category=item.get('category'),
                brand=item.get('brand'),
                unit=item.get('unit'),
                original_price=original_price,
                discount_percentage=discount_percentage,
                start_date=start_date,
                end_date=end_date,
                is_featured_deal=item.get('featured', False),
                description=item.get('description'),
                image_url=item.get('image_url')
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse offer item: {str(e)}")
            return None
    
    def _extract_chain(self, store_name: str) -> str:
        """Extract chain name from store name."""
        name_lower = store_name.lower()
        
        chains = {
            'no frills': 'No Frills',
            'loblaws': 'Loblaws', 
            'metro': 'Metro',
            'sobeys': 'Sobeys',
            'foodland': 'Foodland',
            'freshco': 'FreshCo',
            'giant tiger': 'Giant Tiger',
            'walmart': 'Walmart'
        }
        
        for key, chain in chains.items():
            if key in name_lower:
                return chain
                
        return store_name  # Default to full name
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string into date object."""
        if not date_str:
            return None
            
        try:
            # Try different date formats
            formats = ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
                    
            return None
        except Exception:
            return None


class FlippWebScraper(BaseScraper):
    """Fallback web scraper for Flipp website."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
    @property
    def method(self) -> ScrapingMethod:
        return ScrapingMethod.SELENIUM
    
    def scrape_postal_code(self, postal_code: str) -> ScrapingResult:
        """Scrape Flipp website for postal code."""
        driver = None
        try:
            driver = self._create_driver()
            postal_code = self.clean_postal_code(postal_code)
            
            # Navigate to Flipp grocery page
            driver.get("https://flipp.com/flyers/groceries")
            
            # Wait for page load and input postal code
            wait = WebDriverWait(driver, 10)
            
            # Look for postal code input
            postal_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='postal' i], input[placeholder*='zip' i]"))
            )
            
            postal_input.clear()
            postal_input.send_keys(postal_code)
            postal_input.submit()
            
            # Wait for results to load
            time.sleep(3)
            
            # Extract flyer listings
            stores = []
            flyer_elements = driver.find_elements(By.CSS_SELECTOR, "flipp-flyer-listing-item")
            
            for element in flyer_elements:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, "p.flyer-name")
                    name = name_elem.text.strip()
                    
                    if name and any(word in name.lower() for word in ['grocery', 'market', 'food']):
                        stores.append(StoreData(
                            name=name,
                            chain=self._extract_chain(name),
                            address="",  # Would need additional scraping
                            postal_code=postal_code,
                            website="https://flipp.com"
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Failed to parse flyer element: {str(e)}")
                    continue
            
            return ScrapingResult(
                success=True,
                method_used=self.method,
                stores=stores,
                offers=[],  # Would need to navigate to individual flyers
                metadata={'postal_code': postal_code}
            )
            
        except Exception as e:
            self.logger.error(f"Flipp web scraping failed: {str(e)}")
            return ScrapingResult(
                success=False,
                method_used=self.method,
                stores=[],
                offers=[],
                error_message=str(e)
            )
        finally:
            if driver:
                driver.quit()
    
    def scrape_store(self, store_url: str, store_name: str = None) -> ScrapingResult:
        """Scrape individual store flyer."""
        # Implementation would go here for scraping individual flyer pages
        return ScrapingResult(
            success=False,
            method_used=self.method,
            stores=[],
            offers=[],
            error_message="Individual flyer scraping not yet implemented"
        )
    
    def _create_driver(self):
        """Create configured Chrome WebDriver."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def _extract_chain(self, store_name: str) -> str:
        """Extract chain name from store name."""
        # Same logic as FlippAPIScraper
        name_lower = store_name.lower()
        
        chains = {
            'no frills': 'No Frills',
            'loblaws': 'Loblaws', 
            'metro': 'Metro',
            'sobeys': 'Sobeys',
            'foodland': 'Foodland',
            'freshco': 'FreshCo'
        }
        
        for key, chain in chains.items():
            if key in name_lower:
                return chain
                
        return store_name
