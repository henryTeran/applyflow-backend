"""
Timeline events API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.crud import timeline_event as crud
from app.schemas.timeline_event import TimelineEventCreate, TimelineEventRead

router = APIRouter()


@router.get("/application/{application_id}", response_model=List[TimelineEventRead])
def list_application_timeline(
    application_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all timeline events for a specific application."""
    return crud.list_by_application(
        db,
        application_id=application_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


@router.post("/application/{application_id}", response_model=TimelineEventRead, status_code=201)
def create_timeline_event(
    application_id: int,
    event: TimelineEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new timeline event for an application."""
    # Ensure the application_id in the path matches the one in the body
    if event.application_id != application_id:
        raise HTTPException(
            status_code=400,
            detail="Application ID in path must match application_id in request body"
        )
    
    return crud.create(db, event, current_user.id)


@router.get("/{event_id}", response_model=TimelineEventRead)
def get_timeline_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific timeline event by ID."""
    event = crud.get(db, event_id, current_user.id)
    if not event:
        raise HTTPException(status_code=404, detail="Timeline event not found")
    return event


@router.delete("/{event_id}", status_code=204)
def delete_timeline_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a timeline event."""
    success = crud.delete(db, event_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Timeline event not found")
    return None
