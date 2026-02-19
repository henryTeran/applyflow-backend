"""
CRUD operations for Application model.
"""

from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.models.application import Application
from app.models.timeline_event import TimelineEvent
from app.schemas.application import ApplicationCreate, ApplicationUpdate


def create(db: Session, application: ApplicationCreate, user_id: int) -> Application:
    """Create a new application."""
    db_application = Application(**application.model_dump(), user_id=user_id)
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    # Créer automatiquement un événement de timeline
    timeline_event = TimelineEvent(
        application_id=db_application.id,
        user_id=user_id,
        event_type="application_created",
        event_date=datetime.now(),
        description=f"Candidature créée via {application.channel}"
    )
    db.add(timeline_event)
    db.commit()
    
    return db_application


def get(db: Session, application_id: int, user_id: Optional[int] = None) -> Optional[Application]:
    """Get application by ID."""
    query = db.query(Application).filter(Application.id == application_id)
    if user_id:
        query = query.filter(Application.user_id == user_id)
    return query.first()


def get_by_job_offer(db: Session, job_offer_id: int, user_id: int) -> Optional[Application]:
    """Get application for a specific job offer."""
    return (
        db.query(Application)
        .filter(Application.job_offer_id == job_offer_id)
        .filter(Application.user_id == user_id)
        .first()
    )


def list_applications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    company: Optional[str] = None
) -> list[Application]:
    """List applications with optional filters and pagination."""
    query = db.query(Application).filter(Application.user_id == user_id)
    
    if status:
        query = query.filter(Application.status == status)
    
    # Join with JobOffer to filter by company
    if company:
        from app.models.job_offer import JobOffer
        query = query.join(JobOffer).filter(JobOffer.company.ilike(f"%{company}%"))
    
    return query.order_by(Application.created_at.desc()).offset(skip).limit(limit).all()


def update(db: Session, application_id: int, application_update: ApplicationUpdate, user_id: int) -> Optional[Application]:
    """Update application information."""
    db_application = get(db, application_id, user_id)
    if not db_application:
        return None
    
    update_data = application_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_application, field, value)
    
    db.commit()
    db.refresh(db_application)
    return db_application


def update_status(db: Session, application_id: int, new_status: str, user_id: int) -> Optional[Application]:
    """Update only the status of an application."""
    db_application = get(db, application_id, user_id)
    if not db_application:
        return None
    
    old_status = db_application.status
    db_application.status = new_status
    db.commit()
    db.refresh(db_application)
    
    # Créer un événement de timeline pour le changement de statut
    if old_status != new_status:
        status_descriptions = {
            "sent": "Candidature envoyée",
            "interview": "Entretien programmé",
            "offer": "Offre reçue",
            "rejected": "Candidature refusée",
            "on_hold": "En attente"
        }
        
        timeline_event = TimelineEvent(
            application_id=db_application.id,
            user_id=user_id,
            event_type="status_change",
            event_date=datetime.now(),
            description=f"Statut changé: {old_status} → {new_status}"
        )
        db.add(timeline_event)
        db.commit()
    
    return db_application


def delete(db: Session, application_id: int, user_id: int) -> bool:
    """Delete an application."""
    db_application = get(db, application_id, user_id)
    if not db_application:
        return False
    
    db.delete(db_application)
    db.commit()
    return True
