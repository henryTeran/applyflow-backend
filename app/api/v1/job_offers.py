"""
Job offers API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, field_validator

from app.api.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.crud import job_offer as crud
from app.schemas.job_offer import JobOfferCreate, JobOfferRead, JobOfferUpdate
from app.agents.pipeline_agent import run_job_offer_pipeline, PipelineResult
from app.services.scraping_service import scrape_job_offer, ScrapeResult

router = APIRouter()


def _infer_source_from_url(url: str) -> str:
    u = (url or "").lower()
    if "linkedin.com" in u:
        return "LinkedIn"
    if "indeed." in u:
        return "Indeed"
    if "welcometothejungle.com" in u or "wttj.co" in u:
        return "WelcomeToTheJungle"
    return "Web"


class ScrapeRequest(BaseModel):
    """Request to scrape a job offer URL"""
    url: str
    
    @field_validator('url')
    @classmethod
    def normalize_url(cls, v: str) -> str:
        """Normalize URL by adding https:// if missing"""
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")
        
        # Add https:// if no protocol specified
        if not v.startswith(('http://', 'https://')):
            v = f'https://{v}'
        
        # Basic validation
        if '.' not in v:
            raise ValueError("Invalid URL format")
        
        return v


class CreateFromUrlRequest(BaseModel):
    """Request to create a JobOffer by providing only a URL."""

    url: str
    source: Optional[str] = None

    @field_validator("url")
    @classmethod
    def normalize_url(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")
        if not v.startswith(("http://", "https://")):
            v = f"https://{v}"
        if "." not in v:
            raise ValueError("Invalid URL format")
        return v


@router.post("/", response_model=JobOfferRead, status_code=201)
def create_job_offer(
    job_offer: JobOfferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new job offer."""
    return crud.create(db, job_offer, current_user.id)


@router.post("/scrape", response_model=ScrapeResult)
def scrape_job_posting(
    data: ScrapeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Scrape job offer details from a URL.
    
    Supports: LinkedIn, Indeed, Welcome to the Jungle.
    
    Returns job details without saving to database.
    Frontend can then create the job offer with scraped data.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Scraping request from user {current_user.id}: {data.url}")
    
    try:
        result = scrape_job_offer(str(data.url))
        logger.info(f"Scraping successful: {result.title} at {result.company}")
        return result
    except ValueError as e:
        # Platform not supported
        logger.warning(f"Scraping failed - platform not supported: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Scraping failed
        logger.error(f"Scraping failed - error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to scrape job offer: {str(e)}"
        )


@router.post("/from-url", response_model=JobOfferRead, status_code=201)
def create_job_offer_from_url(
    data: CreateFromUrlRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new job offer by scraping a URL.

    This endpoint is meant for Swagger/UI usage: paste a link, we scrape and
    persist the job offer in one step.
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"Create job offer from URL user={current_user.id}: {data.url}")

    try:
        result = scrape_job_offer(str(data.url))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape job offer: {str(e)}")

    # Basic validation to avoid saving unusable scraped data (common with LinkedIn login wall)
    if not (result.title and result.title.strip()):
        raise HTTPException(
            status_code=400,
            detail="Scraping succeeded but title is empty (likely blocked/partial LinkedIn page).",
        )
    if not (result.company and result.company.strip()):
        raise HTTPException(
            status_code=400,
            detail="Scraping succeeded but company is empty (likely blocked/partial LinkedIn page).",
        )
    if not (result.description and len(result.description.strip()) >= 300):
        raise HTTPException(
            status_code=400,
            detail="Scraping returned a too-short description (likely blocked/partial page).",
        )

    job_offer = JobOfferCreate(
        title=result.title,
        company=result.company,
        location=result.location,
        source=data.source or _infer_source_from_url(str(data.url)),
        url=str(data.url),
        application_type=result.application_type,
        application_url=result.application_url,
        raw_description=result.description,
    )

    return crud.create(db, job_offer, current_user.id)


@router.get("/", response_model=List[JobOfferRead])
def list_job_offers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    company: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all job offers with optional filters."""
    return crud.list_job_offers(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        company=company,
        source=source
    )


@router.get("/{job_offer_id}", response_model=JobOfferRead)
def get_job_offer(
    job_offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific job offer by ID."""
    job_offer = crud.get(db, job_offer_id, current_user.id)
    if not job_offer:
        raise HTTPException(status_code=404, detail="Job offer not found")
    return job_offer


@router.patch("/{job_offer_id}", response_model=JobOfferRead)
def update_job_offer(
    job_offer_id: int,
    job_offer_update: JobOfferUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a job offer."""
    job_offer = crud.update(db, job_offer_id, job_offer_update, current_user.id)
    if not job_offer:
        raise HTTPException(status_code=404, detail="Job offer not found")
    return job_offer


@router.delete("/{job_offer_id}", status_code=204)
def delete_job_offer(
    job_offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a job offer."""
    success = crud.delete(db, job_offer_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Job offer not found")
    return None


@router.post("/{job_offer_id}/run-pipeline")
def run_pipeline(
    job_offer_id: int,
    regenerate: bool = Query(False, description="Regenerate even if match/draft exists"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run the complete pipeline for a job offer:
    1. Compute match score
    2. Generate application draft (cover letter + PDF + email)
    
    Returns the job offer, match, and draft.
    """
    result = run_job_offer_pipeline(job_offer_id, current_user.id, db, regenerate=regenerate)
    
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    
    return {
        "success": result.success,
        "message": result.message,
        "job_offer": {
            "id": result.job_offer.id,
            "title": result.job_offer.title,
            "company": result.job_offer.company,
            "location": result.job_offer.location,
            "source": result.job_offer.source
        },
        "match": {
            "id": result.job_match.id,
            "score": result.job_match.score,
            "reasons": result.job_match.reasons,
            "skills_detected": result.job_match.skills_detected,
            "red_flags": result.job_match.red_flags
        },
        "draft": {
            "id": result.application_draft.id,
            "status": result.application_draft.status,
            "email_subject": result.application_draft.email_subject,
            "cover_letter_pdf_path": result.application_draft.cover_letter_pdf_path
        }
    }
