"""
TimelineEvent model - tracks application lifecycle events.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class TimelineEvent(Base):
    """Timeline event for an application (email sent, interview, note, etc.)."""
    
    __tablename__ = "timeline_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    
    # Event details
    event_type = Column(
        String(50),
        nullable=False
    )  # "email_sent", "portal_submitted", "interview", "note", "reminder", "status_change", etc.
    
    description = Column(Text, nullable=False)
    
    # Event date (can be in the future for reminders)
    event_date = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    application = relationship("Application", back_populates="timeline_events")
    
    # Indexes
    __table_args__ = (
        Index('ix_timeline_events_application_id', 'application_id'),
        Index('ix_timeline_events_event_date', 'event_date'),
        Index('ix_timeline_events_event_type', 'event_type'),
    )
    
    def __repr__(self):
        return f"<TimelineEvent(id={self.id}, application_id={self.application_id}, type='{self.event_type}')>"
