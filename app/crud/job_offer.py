"""
CRUD operations for JobOffer model.
"""

from sqlalchemy.orm import Session
from typing import Optional
from app.models.job_offer import JobOffer
from app.schemas.job_offer import JobOfferCreate, JobOfferUpdate


def create(db: Session, job_offer: JobOfferCreate, user_id: int) -> JobOffer:
    """Create a new job offer."""
    db_job_offer = JobOffer(**job_offer.model_dump(), user_id=user_id)
    db.add(db_job_offer)
    db.commit()
    db.refresh(db_job_offer)
    return db_job_offer


def get(db: Session, job_offer_id: int, user_id: Optional[int] = None) -> Optional[JobOffer]:
    """Get job offer by ID."""
    query = db.query(JobOffer).filter(JobOffer.id == job_offer_id)
    if user_id:
        query = query.filter(JobOffer.user_id == user_id)
    return query.first()


def list_job_offers(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    company: Optional[str] = None,
    source: Optional[str] = None
) -> list[JobOffer]:
    """List job offers with optional filters and pagination."""
    query = db.query(JobOffer).filter(JobOffer.user_id == user_id)
    
    if company:
        query = query.filter(JobOffer.company.ilike(f"%{company}%"))
    
    if source:
        query = query.filter(JobOffer.source == source)
    
    return query.order_by(JobOffer.created_at.desc()).offset(skip).limit(limit).all()


def update(db: Session, job_offer_id: int, job_offer_update: JobOfferUpdate, user_id: int) -> Optional[JobOffer]:
    """Update job offer information."""
    db_job_offer = get(db, job_offer_id, user_id)
    if not db_job_offer:
        return None
    
    update_data = job_offer_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_job_offer, field, value)
    
    db.commit()
    db.refresh(db_job_offer)
    return db_job_offer


def delete(db: Session, job_offer_id: int, user_id: int) -> bool:
    """Delete a job offer."""
    db_job_offer = get(db, job_offer_id, user_id)
    if not db_job_offer:
        return False
    
    db.delete(db_job_offer)
    db.commit()
    return True
