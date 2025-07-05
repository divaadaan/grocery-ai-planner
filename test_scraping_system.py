#!/usr/bin/env python3
"""
Test script for the new scraping system.
Run this to validate that all components are working correctly.
"""

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all scraping modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from scrapers import ScrapingOrchestrator, ScrapingMethod
        print("✅ ScrapingOrchestrator imported successfully")
        
        from scrapers.flipp_scraper import FlippAPIScraper, FlippWebScraper
        print("✅ Flipp scrapers imported successfully")
        
        from scrapers.selenium_scraper import SeleniumScraper
        print("✅ Selenium scraper imported successfully")
        
        from scrapers.base_scraper import BaseScraper, ScrapingResult, OfferData, StoreData
        print("✅ Base scraper classes imported successfully")
        
        from core.config import get_scraping_config
        print("✅ Configuration imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_configuration():
    """Test that configuration is working."""
    print("\n🔧 Testing configuration...")
    
    try:
        from core.config import get_scraping_config
        config = get_scraping_config()
        
        print(f"✅ Configuration loaded successfully")
        print(f"   - Flipp API enabled: {config['flipp_api']['enabled']}")
        print(f"   - Selenium enabled: {config['selenium']['enabled']}")
        print(f"   - PDF OCR enabled: {config['pdf_ocr']['enabled']}")
        print(f"   - Vision AI enabled: {config['vision_ai']['enabled']}")
        print(f"   - Scraping timeout: {config['general']['timeout']}s")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_orchestrator():
    """Test that the scraping orchestrator initializes correctly."""
    print("\n🎭 Testing scraping orchestrator...")
    
    try:
        from scrapers import ScrapingOrchestrator
        orchestrator = ScrapingOrchestrator()
        
        available_methods = orchestrator.get_available_methods()
        print(f"✅ Orchestrator initialized successfully")
        print(f"   - Available methods: {[method.value for method in available_methods]}")
        print(f"   - Total scrapers: {len(orchestrator.scrapers)}")
        
        # Test scraper availability
        test_results = orchestrator.test_scrapers()
        print(f"   - Scraper test results:")
        for method, available in test_results.items():
            status = "✅" if available else "❌"
            print(f"     {status} {method.value}: {'Available' if available else 'Not available'}")
        
        return True
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False

def test_dependencies():
    """Test that required dependencies are available."""
    print("\n📦 Testing dependencies...")
    
    dependencies = [
        ('selenium', 'Selenium WebDriver'),
        ('webdriver_manager', 'WebDriver Manager'),
        ('requests', 'HTTP Requests'),
        ('lxml', 'XML/HTML Parser')
    ]
    
    all_available = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name} available")
        except ImportError:
            print(f"❌ {name} not available")
            all_available = False
    
    # Test optional dependencies
    optional_deps = [
        ('pytesseract', 'OCR (Tesseract)'),
        ('PIL', 'Image processing (Pillow)')
    ]
    
    for module, name in optional_deps:
        try:
            __import__(module)
            print(f"✅ {name} available (optional)")
        except ImportError:
            print(f"⚠️  {name} not available (optional)")
    
    return all_available

def test_database_models():
    """Test that database models are compatible."""
    print("\n🗄️ Testing database models...")
    
    try:
        from core.models import Store, CurrentOffer, ScrapeJob
        print("✅ Store model imported")
        print("✅ CurrentOffer model imported")
        print("✅ ScrapeJob model imported")
        
        # Check that models have required fields for new system
        store_fields = ['scrape_config', 'last_scraped', 'chain']
        offer_fields = ['category', 'discount_percentage', 'is_featured_deal']
        
        for field in store_fields:
            if hasattr(Store, field):
                print(f"✅ Store.{field} field available")
            else:
                print(f"❌ Store.{field} field missing")
        
        for field in offer_fields:
            if hasattr(CurrentOffer, field):
                print(f"✅ CurrentOffer.{field} field available")
            else:
                print(f"❌ CurrentOffer.{field} field missing")
        
        return True
    except Exception as e:
        print(f"❌ Database model test failed: {e}")
        return False

def test_secrets():
    """Test that Docker secrets are properly configured."""
    print("\n🔐 Testing Docker secrets...")

    try:
        from core.secrets import SecretsManager

        # Test secrets manager
        available_secrets = SecretsManager.list_available_secrets()
        print(f"✅ Secrets manager working, found {len(available_secrets)} secrets")

        # Test required secrets
        required_secrets = ['database_url', 'redis_url', 'secret_key', 'llm_api_url']
        missing_secrets = []

        for secret in required_secrets:
            try:
                value = SecretsManager.get_secret(secret)
                if value:
                    print(f"✅ {secret}: configured")
                else:
                    print(f"❌ {secret}: empty")
                    missing_secrets.append(secret)
            except Exception as e:
                print(f"❌ {secret}: {str(e)}")
                missing_secrets.append(secret)

        if missing_secrets:
            print(f"⚠️  Missing secrets: {missing_secrets}")
            print("Run: ./scripts/setup-secrets.sh")
            return False

        return True
    except ImportError as e:
        print(f"❌ Secrets manager import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing New Scraping System")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_dependencies,
        test_configuration,
        test_database_models,
        test_orchestrator
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The new scraping system is ready.")
        print("\n💡 Next steps:")
        print("   1. Start the application: docker-compose up -d")
        print("   2. Test the API: curl -X POST http://localhost:8000/api/v1/scraping/test")
        print("   3. Try postal code scraping: curl -X POST http://localhost:8000/api/v1/scraping/postal-code -H 'Content-Type: application/json' -d '{\"postal_code\": \"M5V 3A8\"}'")
    else:
        print("⚠️  Some tests failed. Please check the output above and fix any issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()
