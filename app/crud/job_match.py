"""
CRUD operations for JobMatch model.
"""

from sqlalchemy.orm import Session
from typing import Optional
from app.models.job_match import JobMatch
from app.schemas.job_match import JobMatchCreate


def create(db: Session, job_match: JobMatchCreate, user_id: int) -> JobMatch:
    """Create a new job match."""
    db_job_match = JobMatch(**job_match.model_dump(), user_id=user_id)
    db.add(db_job_match)
    db.commit()
    db.refresh(db_job_match)
    return db_job_match


def get(db: Session, job_match_id: int, user_id: Optional[int] = None) -> Optional[JobMatch]:
    """Get job match by ID."""
    query = db.query(JobMatch).filter(JobMatch.id == job_match_id)
    if user_id:
        query = query.filter(JobMatch.user_id == user_id)
    return query.first()


def get_by_job_offer(db: Session, job_offer_id: int, user_id: int) -> Optional[JobMatch]:
    """Get job match for a specific job offer (usually the most recent one)."""
    return (
        db.query(JobMatch)
        .filter(JobMatch.job_offer_id == job_offer_id)
        .filter(JobMatch.user_id == user_id)
        .order_by(JobMatch.created_at.desc())
        .first()
    )


def list_job_matches(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    job_offer_id: Optional[int] = None,
    min_score: Optional[float] = None
) -> list[JobMatch]:
    """List job matches with optional filters and pagination."""
    query = db.query(JobMatch).filter(JobMatch.user_id == user_id)
    
    if job_offer_id:
        query = query.filter(JobMatch.job_offer_id == job_offer_id)
    
    if min_score is not None:
        query = query.filter(JobMatch.score >= min_score)
    
    return query.order_by(JobMatch.created_at.desc()).offset(skip).limit(limit).all()


def delete(db: Session, job_match_id: int, user_id: int) -> bool:
    """Delete a job match."""
    db_job_match = get(db, job_match_id, user_id)
    if not db_job_match:
        return False
    
    db.delete(db_job_match)
    db.commit()
    return True
