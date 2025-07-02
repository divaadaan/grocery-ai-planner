# backend/scrapers/__init__.py
"""Scraping framework for grocery deal collection."""

from .base_scraper import BaseScraper, ScrapingResult, ScrapingMethod
from .flipp_scraper import FlippAPIScraper, FlippWebScraper
from .selenium_scraper import SeleniumScraper
from .pdf_scraper import PDFScraper
from .vision_scraper import VisionScraper
from .scraping_orchestrator import ScrapingOrchestrator

__all__ = [
    'BaseScraper',
    'ScrapingResult', 
    'ScrapingMethod',
    'FlippAPIScraper',
    'FlippWebScraper',
    'SeleniumScraper',
    'PDFScraper',
    'VisionScraper',
    'ScrapingOrchestrator'
]
