"""
JobMatch model - stores matching score between job and candidate.
"""

from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class JobMatch(Base):
    """Match analysis between a job offer and candidate profile."""
    
    __tablename__ = "job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_offer_id = Column(Integer, ForeignKey("job_offers.id", ondelete="CASCADE"), nullable=False)
    
    # Match score (0-100)
    score = Column(Float, nullable=False)
    
    # Analysis details
    reasons = Column(Text, nullable=True)  # Why this score
    skills_detected = Column(Text, nullable=True)  # JSON or comma-separated
    red_flags = Column(Text, nullable=True)  # JSON or comma-separated
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    job_offer = relationship("JobOffer", back_populates="matches")
    
    # Indexes
    __table_args__ = (
        Index('ix_job_matches_job_offer_id', 'job_offer_id'),
        Index('ix_job_matches_score', 'score'),
    )
    
    def __repr__(self):
        return f"<JobMatch(id={self.id}, job_offer_id={self.job_offer_id}, score={self.score})>"
