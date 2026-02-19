"""
Application drafts API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.crud import application_draft as crud
from app.schemas.application_draft import ApplicationDraftRead, ApplicationDraftUpdate, ApplicationDraftCreate

router = APIRouter()


@router.post("/", response_model=ApplicationDraftRead, status_code=201)
def create_draft(
    draft: ApplicationDraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new application draft."""
    return crud.create(db, draft, current_user.id)


@router.get("/", response_model=List[ApplicationDraftRead])
def list_drafts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    job_offer_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all application drafts with optional filters."""
    return crud.list_drafts(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        job_offer_id=job_offer_id,
        status=status
    )


@router.get("/by-job/{job_offer_id}", response_model=ApplicationDraftRead)
def get_draft_by_job_offer(
    job_offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get application draft by job offer ID."""
    drafts = crud.list_drafts(db, user_id=current_user.id, job_offer_id=job_offer_id, limit=1)
    if not drafts:
        raise HTTPException(status_code=404, detail="No draft found for this job offer")
    return drafts[0]


@router.post("/generate/{job_offer_id}", response_model=ApplicationDraftRead, status_code=201)
def generate_draft(
    job_offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a new application draft for a job offer."""
    from app.services.draft_service import generate_application_draft
    import logging
    logger = logging.getLogger(__name__)
    
    # Check if user has uploaded CV (check both new and old fields for backward compatibility)
    if not current_user.cv_file_path and not current_user.cv_text and not current_user.cv_path:
        raise HTTPException(
            status_code=400,
            detail="You must upload your CV first. Please go to your profile to upload your CV."
        )
    
    # Check if draft already exists
    existing_drafts = crud.list_drafts(db, user_id=current_user.id, job_offer_id=job_offer_id, limit=1)
    if existing_drafts:
        return existing_drafts[0]
    
    # Generate new draft
    try:
        draft = generate_application_draft(job_offer_id, current_user.id, db)
        return draft
    except ValueError as e:
        # Job offer or user not found
        logger.warning(f"Draft generation failed - not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate draft for job {job_offer_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate draft: {str(e)}")


@router.get("/{job_offer_id}", response_model=ApplicationDraftRead)
def get_draft_by_job_or_id(
    job_offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get draft by job offer ID or draft ID.
    First tries to find a draft by job_offer_id, then by draft id.
    """
    # Try to find by job_offer_id first
    drafts = crud.list_drafts(db, user_id=current_user.id, job_offer_id=job_offer_id, limit=1)
    if drafts:
        return drafts[0]
    
    # Try to find by draft id
    draft = crud.get(db, job_offer_id, current_user.id)
    if draft:
        return draft
    
    raise HTTPException(status_code=404, detail="Draft not found")


@router.post("/{job_offer_id}", response_model=ApplicationDraftRead, status_code=201)
def create_or_get_draft(
    job_offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate or get existing draft for a job offer."""
    from app.services.draft_service import generate_application_draft
    
    # Check if user has uploaded CV
    if not current_user.cv_file_path and not current_user.cv_text:
        raise HTTPException(
            status_code=400,
            detail="You must upload your CV first. Please go to your profile to upload your CV."
        )
    
    # Check if draft already exists
    existing_drafts = crud.list_drafts(db, user_id=current_user.id, job_offer_id=job_offer_id, limit=1)
    if existing_drafts:
        return existing_drafts[0]
    
    # Generate new draft
    try:
        draft = generate_application_draft(job_offer_id, current_user.id, db)
        return draft
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate draft: {str(e)}")


@router.patch("/{draft_id}", response_model=ApplicationDraftRead)
def update_draft(
    draft_id: int,
    draft_update: ApplicationDraftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an application draft."""
    draft = crud.update(db, draft_id, draft_update, current_user.id)
    if not draft:
        raise HTTPException(status_code=404, detail="Application draft not found")
    return draft


@router.delete("/{draft_id}", status_code=204)
def delete_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an application draft."""
    success = crud.delete(db, draft_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Application draft not found")
    return None


@router.post("/{draft_id}/send", status_code=200)
def send_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a draft (mark as sent by creating an application).
    This endpoint converts a draft into a real application.
    """
    from app.crud import application as application_crud
    from app.schemas.application import ApplicationCreate
    
    # Get the draft with ownership check
    draft = crud.get(db, draft_id, current_user.id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    # Check if application already exists for this job offer
    existing_app = application_crud.get_by_job_offer(db, draft.job_offer_id, current_user.id)
    if existing_app:
        return {
            "success": True,
            "message": "Application already sent",
            "application_id": existing_app.id
        }
    
    # Create application
    application_data = ApplicationCreate(
        job_offer_id=draft.job_offer_id,
        channel="email",
        status="sent"
    )
    
    application = application_crud.create(db, application_data, current_user.id)
    
    # Update draft status
    from app.schemas.application_draft import ApplicationDraftUpdate
    draft_update = ApplicationDraftUpdate(status="sent")
    crud.update(db, draft_id, draft_update, current_user.id)
    
    return {
        "success": True,
        "message": "Application sent successfully",
        "application_id": application.id,
        "draft_id": draft_id
    }
