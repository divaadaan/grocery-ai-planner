# backend/core/models/offer.py
from sqlalchemy import Column, Integer, String, Float, Text, Date, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class CurrentOffer(Base, TimestampMixin):
    __tablename__ = "current_offers"
    
    offer_id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    
    # Product details
    product_name = Column(String(255), nullable=False)
    brand = Column(String(100))
    category = Column(String(50), index=True)  # "produce", "meat", "dairy", etc.
    subcategory = Column(String(50))
    
    # Pricing
    price = Column(Float, nullable=False)
    original_price = Column(Float)  # If on sale
    unit = Column(String(20))  # "lb", "kg", "each", "pkg", etc.
    unit_price = Column(Float)  # Price per standard unit
    
    # Offer details
    is_featured_deal = Column(Boolean, default=False)
    discount_percentage = Column(Integer)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Additional info
    description = Column(Text)
    image_url = Column(String(500))
    organic = Column(Boolean, default=False)
    
    # Relationships
    store = relationship("Store", back_populates="offers")
    
    def __repr__(self):
        return f"<CurrentOffer(product='{self.product_name}', price={self.price})>"

# Add composite index for efficient queries
Index('idx_offers_store_category_date', 
      CurrentOffer.store_id, 
      CurrentOffer.category, 
      CurrentOffer.start_date, 
      CurrentOffer.end_date)