# backend/core/models/store.py
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum

class PostalCodeStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active" 
    FAILED = "failed"

class PostalCode(Base, TimestampMixin):
    __tablename__ = "postal_codes"
    
    postal_code = Column(String(10), primary_key=True)
    status = Column(Enum(PostalCodeStatus), default=PostalCodeStatus.PENDING)
    last_updated = Column(DateTime)
    error_message = Column(Text)
    
    # Relationships
    stores = relationship("Store", back_populates="postal_code_ref")

class Store(Base, TimestampMixin):
    __tablename__ = "stores"
    
    store_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    chain = Column(String(100))  # "Metro", "Loblaws", etc.
    
    # Location
    address = Column(Text, nullable=False)
    postal_code = Column(String(10), nullable=False, index=True)
    latitude = Column(String(20))
    longitude = Column(String(20))
    
    # Contact/Web
    phone = Column(String(20))
    website = Column(String(500))
    flyer_url = Column(String(500))
    
    # Scraping configuration
    scrape_config = Column(JSON, default=dict)  # Store-specific scraping settings
    is_active = Column(Boolean, default=True)
    last_scraped = Column(DateTime)
    scrape_success_rate = Column(Integer, default=0)  # Percentage
    
    # Relationships
    postal_code_ref = relationship("PostalCode", back_populates="stores")
    offers = relationship("CurrentOffer", back_populates="store")
    
    def __repr__(self):
        return f"<Store(name='{self.name}', address='{self.address}')>"