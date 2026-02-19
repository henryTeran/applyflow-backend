"""
Pydantic schemas for Application model.
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ApplicationBase(BaseModel):
    """Base application schema with shared fields."""
    channel: str  # "email", "portal", "mixed"
    portal_type: Optional[str] = None
    submitted_by: str = "manual"  # "bot", "manual"
    reference_number: Optional[str] = None
    confirmation_file_path: Optional[str] = None
    status: str = "sent"  # "sent", "interview", "offer", "rejected", "on_hold"
    sent_at: Optional[datetime] = None
    next_action_date: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    """Schema for creating a new application."""
    job_offer_id: int


class ApplicationUpdate(BaseModel):
    """Schema for updating application."""
    channel: Optional[str] = None
    portal_type: Optional[str] = None
    reference_number: Optional[str] = None
    confirmation_file_path: Optional[str] = None
    status: Optional[str] = None
    sent_at: Optional[datetime] = None
    next_action_date: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    """Schema for updating only the status of an application."""
    status: str


class ApplicationRead(ApplicationBase):
    """Schema for reading application data."""
    id: int
    job_offer_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
