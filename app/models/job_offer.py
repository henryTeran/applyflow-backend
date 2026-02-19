"""
JobOffer model - represents a job posting.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class JobOffer(Base):
    """Job offer/posting with all relevant details."""
    
    __tablename__ = "job_offers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    source = Column(String(100), nullable=False)  # "LinkedIn", "Jobup", "CERN Careers", etc.
    url = Column(String(1000), nullable=True)
    
    # Application details
    application_type = Column(
        String(50),
        nullable=False,
        default="email"
    )  # "email", "portal", "linkedin_easy_apply", "manual"
    application_url = Column(String(1000), nullable=True)
    
    # Job description
    raw_description = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    matches = relationship("JobMatch", back_populates="job_offer", cascade="all, delete-orphan")
    drafts = relationship("ApplicationDraft", back_populates="job_offer", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job_offer", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_job_offers_company_title', 'company', 'title'),
        Index('ix_job_offers_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<JobOffer(id={self.id}, title='{self.title}', company='{self.company}')>"
