"""
Pydantic schemas for JobMatch model.
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class JobMatchBase(BaseModel):
    """Base job match schema with shared fields."""
    score: float = Field(..., ge=0.0, le=100.0, description="Match score from 0 to 100")
    reasons: Optional[str] = None
    skills_detected: Optional[str] = None
    red_flags: Optional[str] = None


class JobMatchCreate(JobMatchBase):
    """Schema for creating a new job match."""
    job_offer_id: int


class JobMatchRead(JobMatchBase):
    """Schema for reading job match data."""
    id: int
    job_offer_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
