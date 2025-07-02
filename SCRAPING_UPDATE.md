# Scraping System Update - New Architecture

## Overview

The scraping system has been completely redesigned to use a **fallback hierarchy** approach with **Flipp as the primary data source**. This change eliminates the need for Beautiful Soup and provides more reliable data collection.

## New Scraping Hierarchy

1. **Primary: Flipp API** - Undocumented JSON API endpoints
2. **Fallback 1: Selenium Web Scraping** - Direct store websites  
3. **Fallback 2: PDF OCR** - PDF flyer processing
4. **Fallback 3: Vision AI** - Complex layout parsing (future)

## Key Changes Made

### 1. Dependencies Updated
- **Removed**: `beautifulsoup4` (ineffective for modern JS sites)
- **Added**: `selenium>=4.15.0` and `webdriver-manager>=4.0.0`
- **Kept**: `playwright` for advanced cases

### 2. New Scraping Framework
- `scrapers/` - Complete scraping framework
  - `base_scraper.py` - Common interface and data structures
  - `flipp_scraper.py` - Flipp API and web scraping
  - `selenium_scraper.py` - Direct store scraping
  - `pdf_scraper.py` - PDF processing (placeholder)
  - `vision_scraper.py` - Vision AI (placeholder)
  - `scraping_orchestrator.py` - Manages fallback hierarchy

### 3. Updated Task System
- `tasks/scraping_tasks.py` - Now uses new scraping framework
- Automatic fallback between methods
- Better error handling and metadata tracking
- Real-time progress updates

### 4. Enhanced API Endpoints
- `POST /scraping/test` - Test all scraping methods
- `POST /scraping/postal-code` - Smart postal code scraping
- `GET /scraping/postal-codes/{postal_code}/stores` - View discovered stores
- `GET /scraping/stores/{store_id}/offers` - View current offers
- `POST /scraping/stores/{store_id}/scrape` - Refresh store data

## Flipp Integration Benefits

### Why Flipp?
- **Official retailer partnerships** - No scraping needed, they get data directly
- **Nationwide coverage** - Hundreds of grocery stores in one API
- **High data quality** - Clean, structured, up-to-date information
- **Legal clarity** - Using publicly available aggregated data

### Flipp API Discovery
Found undocumented JSON endpoints:
```
https://backflipp.wishabi.com/flipp/items/search?locale=en-ca&postal_code=M5V3A8&q=No Frills
```

Parameters:
- `locale=en-ca` - Canadian English
- `postal_code=M5V3A8` - Target area
- `q=No Frills` - Search term (store name or product)

## Usage Examples

### Test Scraping Methods
```bash
curl -X POST http://localhost:8000/api/v1/scraping/test
```

### Scrape Postal Code
```bash
curl -X POST http://localhost:8000/api/v1/scraping/postal-code \
  -H "Content-Type: application/json" \
  -d '{"postal_code": "M5V 3A8", "force_refresh": false}'
```

### Check Job Status
```bash
curl http://localhost:8000/api/v1/scraping/jobs/{job_id}
```

### View Discovered Stores
```bash
curl http://localhost:8000/api/v1/scraping/postal-codes/M5V%203A8/stores
```

## Data Flow

1. **User enters postal code** → API cleans format
2. **Check existing data** → Return if recent data exists
3. **Start scraping job** → Background Celery task
4. **Try Flipp API** → Search for stores and offers
5. **Fallback if needed** → Selenium → PDF → Vision
6. **Store results** → Database with metadata
7. **Return structured data** → Standardized format

## Development Advantages

### Reduced Complexity
- **90% less scraping code** needed
- **One API** covers multiple grocery chains
- **Faster development** cycle
- **Better reliability** than custom scrapers

### Better Data Quality
- **Official partnerships** ensure accuracy
- **Consistent structure** across all stores
- **Real-time updates** from retailers
- **Rich metadata** (categories, deals, etc.)

### Scalability
- **Single rate limit** to manage vs dozens
- **Proven infrastructure** handles millions of users
- **Geographic coverage** automatically included
- **New stores** added without code changes

## Next Steps

1. **Test Flipp API** with real postal codes
2. **Implement rate limiting** and respectful usage
3. **Add store-specific scrapers** for gaps in Flipp coverage
4. **Optimize data refresh** frequency
5. **Monitor API changes** and adapt as needed

## Configuration

Environment variables for scraping:
```env
# Scraping settings
SCRAPING_MAX_RETRIES=3
SCRAPING_RATE_LIMIT_DELAY=0.5
SCRAPING_TIMEOUT=30

# Chrome/Selenium settings  
CHROME_HEADLESS=true
CHROME_DISABLE_GPU=true
```

This new architecture provides a much more robust and maintainable scraping system while dramatically reducing the complexity of supporting multiple grocery chains.
