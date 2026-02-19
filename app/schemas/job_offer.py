"""
Pydantic schemas for JobOffer model.
"""

from pydantic import BaseModel, HttpUrl, ConfigDict
from datetime import datetime
from typing import Optional


class JobOfferBase(BaseModel):
    """Base job offer schema with shared fields."""
    title: str
    company: str
    location: Optional[str] = None
    source: str
    url: Optional[str] = None
    application_type: str = "email"  # "email", "portal", "linkedin_easy_apply", "manual"
    application_url: Optional[str] = None
    raw_description: str


class JobOfferCreate(JobOfferBase):
    """Schema for creating a new job offer."""
    pass


class JobOfferUpdate(BaseModel):
    """Schema for updating job offer information."""
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    application_type: Optional[str] = None
    application_url: Optional[str] = None
    raw_description: Optional[str] = None


class JobOfferRead(JobOfferBase):
    """Schema for reading job offer data."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
