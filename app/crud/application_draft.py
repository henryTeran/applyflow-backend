"""
CRUD operations for ApplicationDraft model.
"""

from sqlalchemy.orm import Session
from typing import Optional
from app.models.application_draft import ApplicationDraft
from app.schemas.application_draft import ApplicationDraftCreate, ApplicationDraftUpdate


def create(db: Session, draft: ApplicationDraftCreate, user_id: int) -> ApplicationDraft:
    """Create a new application draft."""
    db_draft = ApplicationDraft(**draft.model_dump(), user_id=user_id)
    db.add(db_draft)
    db.commit()
    db.refresh(db_draft)
    return db_draft


def get(db: Session, draft_id: int, user_id: Optional[int] = None) -> Optional[ApplicationDraft]:
    """Get application draft by ID."""
    query = db.query(ApplicationDraft).filter(ApplicationDraft.id == draft_id)
    if user_id:
        query = query.filter(ApplicationDraft.user_id == user_id)
    return query.first()


def get_by_job_offer(db: Session, job_offer_id: int, user_id: int) -> Optional[ApplicationDraft]:
    """Get most recent draft for a specific job offer."""
    return (
        db.query(ApplicationDraft)
        .filter(ApplicationDraft.job_offer_id == job_offer_id)
        .filter(ApplicationDraft.user_id == user_id)
        .order_by(ApplicationDraft.created_at.desc())
        .first()
    )


def list_drafts(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    job_offer_id: Optional[int] = None,
    status: Optional[str] = None
) -> list[ApplicationDraft]:
    """List application drafts with optional filters and pagination."""
    query = db.query(ApplicationDraft).filter(ApplicationDraft.user_id == user_id)
    
    if job_offer_id:
        query = query.filter(ApplicationDraft.job_offer_id == job_offer_id)
    
    if status:
        query = query.filter(ApplicationDraft.status == status)
    
    return query.order_by(ApplicationDraft.created_at.desc()).offset(skip).limit(limit).all()


def update(db: Session, draft_id: int, draft_update: ApplicationDraftUpdate, user_id: int) -> Optional[ApplicationDraft]:
    """Update application draft."""
    db_draft = get(db, draft_id, user_id)
    if not db_draft:
        return None
    
    update_data = draft_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_draft, field, value)
    
    db.commit()
    db.refresh(db_draft)
    return db_draft


def delete(db: Session, draft_id: int) -> bool:
    """Delete an application draft."""
    db_draft = get(db, draft_id)
    if not db_draft:
        return False
    
    db.delete(db_draft)
    db.commit()
    return True
