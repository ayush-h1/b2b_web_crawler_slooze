from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ProductItem(BaseModel):
    site: str
    category: str
    title: Optional[str] = None
    price_text: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    currency: Optional[str] = None
    moq: Optional[str] = None
    unit: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_location: Optional[str] = None
    supplier_years: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    url: Optional[str] = None
    product_page_url: Optional[str] = None
    images: List[str] = []
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
