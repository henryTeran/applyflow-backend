"""
ApplicationDraft model - generated application materials.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ApplicationDraft(Base):
    """Draft application materials (cover letter, email, etc.)."""
    
    __tablename__ = "application_drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_offer_id = Column(Integer, ForeignKey("job_offers.id", ondelete="CASCADE"), nullable=False)
    
    # Cover letter
    cover_letter_text = Column(Text, nullable=True)
    cover_letter_pdf_path = Column(String(500), nullable=True)
    
    # Email draft
    email_subject = Column(String(500), nullable=True)
    email_body = Column(Text, nullable=True)
    
    # Attachments (JSON array of file paths)
    attachments = Column(Text, nullable=True)  # Store as JSON string
    
    # Status
    status = Column(
        String(20),
        nullable=False,
        default="draft"
    )  # "draft", "ready"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    job_offer = relationship("JobOffer", back_populates="drafts")
    
    # Indexes
    __table_args__ = (
        Index('ix_application_drafts_job_offer_id', 'job_offer_id'),
        Index('ix_application_drafts_status', 'status'),
    )
    
    def __repr__(self):
        return f"<ApplicationDraft(id={self.id}, job_offer_id={self.job_offer_id}, status='{self.status}')>"
