"""
Pydantic schemas for TimelineEvent model.
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TimelineEventBase(BaseModel):
    """Base timeline event schema with shared fields."""
    event_type: str  # "email_sent", "portal_submitted", "interview", "note", "reminder", etc.
    description: str
    event_date: datetime


class TimelineEventCreate(TimelineEventBase):
    """Schema for creating a new timeline event."""
    application_id: int


class TimelineEventRead(TimelineEventBase):
    """Schema for reading timeline event data."""
    id: int
    application_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
