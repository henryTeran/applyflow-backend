"""
Job matches API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db
from app.api.v1.auth import get_current_user
from app.crud import job_match as crud
from app.schemas.job_match import JobMatchRead

router = APIRouter()


@router.get("/", response_model=List[JobMatchRead])
def list_job_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    job_offer_id: Optional[int] = None,
    min_score: Optional[float] = Query(None, ge=0, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all job matches with optional filters."""
    return crud.list_job_matches(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        job_offer_id=job_offer_id,
        min_score=min_score
    )


@router.get("/by-job/{job_offer_id}", response_model=JobMatchRead)
def get_match_by_job_offer(
    job_offer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get job match by job offer ID."""
    matches = crud.list_job_matches(db, user_id=current_user.id, job_offer_id=job_offer_id, limit=1)
    if not matches:
        raise HTTPException(status_code=404, detail="No match found for this job offer")
    return matches[0]


@router.post("/analyze/{job_offer_id}", response_model=JobMatchRead, status_code=201)
def analyze_job_match(
    job_offer_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze and create a job match score for a job offer using user's profile/CV."""
    from app.services.match_service import calculate_job_match
    
    # Check if user has uploaded CV (check both new and old fields for backward compatibility)
    if not current_user.cv_file_path and not current_user.cv_text and not current_user.cv_path:
        raise HTTPException(
            status_code=400,
            detail="You must upload your CV first. Please go to your profile to upload your CV."
        )
    
    # Check if match already exists for this user
    existing_matches = crud.list_job_matches(db, user_id=current_user.id, job_offer_id=job_offer_id, limit=1)
    if existing_matches:
        return existing_matches[0]
    
    # Calculate new match with user's profile
    try:
        job_match = calculate_job_match(job_offer_id, current_user.id, db)
        return job_match
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze match: {str(e)}")


@router.get("/{job_offer_id}", response_model=JobMatchRead)
def get_match_by_job_or_id(
    job_offer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get match by job offer ID or match ID.
    First tries to find by job_offer_id, then by match id.
    """
    # Try to find by job_offer_id first
    matches = crud.list_job_matches(db, user_id=current_user.id, job_offer_id=job_offer_id, limit=1)
    if matches:
        return matches[0]
    
    # Try to find by match id
    job_match = crud.get(db, job_offer_id, current_user.id)
    if job_match:
        return job_match
    
    raise HTTPException(status_code=404, detail="Job match not found")


@router.delete("/{job_match_id}", status_code=204)
def delete_job_match(
    job_match_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a job match."""
    success = crud.delete(db, job_match_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Job match not found")
    return None
