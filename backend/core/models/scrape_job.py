# backend/core/models/scrape_job.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON
from .base import Base, TimestampMixin
import enum

class ScrapeJobStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ScrapeJob(Base, TimestampMixin):
    __tablename__ = "scrape_jobs"
    
    job_id = Column(Integer, primary_key=True, index=True)
    postal_code = Column(String(10), nullable=False, index=True)
    
    # Job details
    status = Column(Enum(ScrapeJobStatus), default=ScrapeJobStatus.PENDING)
    job_type = Column(String(50), default="store_discovery")  # "store_discovery", "offer_scrape"
    
    # Execution details
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Results and logging
    stores_found = Column(Integer, default=0)
    offers_scraped = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    error_log = Column(JSON, default=list)  # List of error messages
    
    # Configuration
    config = Column(JSON, default=dict)  # Job-specific settings
    
    def __repr__(self):
        return f"<ScrapeJob(postal_code='{self.postal_code}', status='{self.status}')>"