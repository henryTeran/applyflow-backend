"""
CRUD operations for TimelineEvent model.
"""

from sqlalchemy.orm import Session
from typing import Optional
from app.models.timeline_event import TimelineEvent
from app.schemas.timeline_event import TimelineEventCreate


def create(db: Session, event: TimelineEventCreate, user_id: int) -> TimelineEvent:
    """Create a new timeline event."""
    db_event = TimelineEvent(**event.model_dump(), user_id=user_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get(db: Session, event_id: int, user_id: Optional[int] = None) -> Optional[TimelineEvent]:
    """Get timeline event by ID."""
    query = db.query(TimelineEvent).filter(TimelineEvent.id == event_id)
    if user_id:
        query = query.filter(TimelineEvent.user_id == user_id)
    return query.first()


def list_by_application(
    db: Session,
    application_id: int,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[TimelineEvent]:
    """List all timeline events for a specific application."""
    return (
        db.query(TimelineEvent)
        .filter(TimelineEvent.application_id == application_id)
        .filter(TimelineEvent.user_id == user_id)
        .order_by(TimelineEvent.event_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def list_events(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None
) -> list[TimelineEvent]:
    """List timeline events with optional filters and pagination."""
    query = db.query(TimelineEvent).filter(TimelineEvent.user_id == user_id)
    
    if event_type:
        query = query.filter(TimelineEvent.event_type == event_type)
    
    return query.order_by(TimelineEvent.event_date.desc()).offset(skip).limit(limit).all()


def delete(db: Session, event_id: int, user_id: int) -> bool:
    """Delete a timeline event."""
    db_event = get(db, event_id, user_id)
    if not db_event:
        return False
    
    db.delete(db_event)
    db.commit()
    return True
