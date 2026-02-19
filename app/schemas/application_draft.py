"""
Pydantic schemas for ApplicationDraft model.
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ApplicationDraftBase(BaseModel):
    """Base application draft schema with shared fields."""
    cover_letter_text: Optional[str] = None
    cover_letter_pdf_path: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    attachments: Optional[str] = None  # JSON string
    status: str = "draft"  # "draft", "ready"


class ApplicationDraftCreate(ApplicationDraftBase):
    """Schema for creating a new application draft."""
    job_offer_id: int


class ApplicationDraftUpdate(BaseModel):
    """Schema for updating application draft."""
    cover_letter_text: Optional[str] = None
    cover_letter_pdf_path: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    attachments: Optional[str] = None
    status: Optional[str] = None


class ApplicationDraftRead(ApplicationDraftBase):
    """Schema for reading application draft data."""
    id: int
    job_offer_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
