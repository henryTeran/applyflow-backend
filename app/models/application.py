"""
Application model - tracks submitted job applications.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Application(Base):
    """Submitted job application with tracking information."""
    
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_offer_id = Column(Integer, ForeignKey("job_offers.id", ondelete="CASCADE"), nullable=False)
    
    # Submission details
    channel = Column(
        String(20),
        nullable=False
    )  # "email", "portal", "mixed"
    
    portal_type = Column(String(50), nullable=True)  # "cern", "hug", "generic", etc.
    
    submitted_by = Column(
        String(20),
        nullable=False,
        default="manual"
    )  # "bot", "manual"
    
    # Reference and confirmation
    reference_number = Column(String(255), nullable=True)
    confirmation_file_path = Column(String(500), nullable=True)
    
    # Status tracking
    status = Column(
        String(20),
        nullable=False,
        default="sent"
    )  # "sent", "interview", "offer", "rejected", "on_hold"
    
    # Important dates
    sent_at = Column(DateTime(timezone=True), nullable=True)
    next_action_date = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    job_offer = relationship("JobOffer", back_populates="applications")
    timeline_events = relationship("TimelineEvent", back_populates="application", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_applications_job_offer_id', 'job_offer_id'),
        Index('ix_applications_status', 'status'),
        Index('ix_applications_sent_at', 'sent_at'),
        Index('ix_applications_next_action_date', 'next_action_date'),
    )
    
    def __repr__(self):
        return f"<Application(id={self.id}, job_offer_id={self.job_offer_id}, status='{self.status}')>"
