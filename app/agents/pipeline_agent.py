"""
Pipeline agent - orchestrates the complete job offer processing pipeline.
"""

from dataclasses import dataclass
from sqlalchemy.orm import Session

from app.models.job_offer import JobOffer
from app.models.job_match import JobMatch
from app.models.application_draft import ApplicationDraft
from app.crud import job_offer as job_offer_crud
from app.crud import job_match as job_match_crud
from app.services.match_service import compute_match_score, extract_profile_from_user
from app.services.draft_service import draft_service
from app.schemas.job_match import JobMatchCreate


@dataclass
class PipelineResult:
    """Result of running the job offer pipeline."""
    job_offer: JobOffer
    job_match: JobMatch
    application_draft: ApplicationDraft
    success: bool
    message: str


def run_job_offer_pipeline(
    job_offer_id: int,
    user_id: int,
    db: Session,
    regenerate: bool = False
) -> PipelineResult:
    """
    Run the complete pipeline for a job offer:
    1. Fetch the job offer
    2. Compute match score
    3. Create JobMatch record
    4. Generate application draft (cover letter + PDF + email)
    5. Create ApplicationDraft record
    
    Args:
        job_offer_id: ID of the job offer to process
        user_id: ID of the user
        db: Database session
        regenerate: If True, regenerate match and draft even if they exist
    
    Returns:
        PipelineResult with all generated data
    """
    # Step 1: Fetch job offer with user_id filter
    job_offer = job_offer_crud.get(db, job_offer_id, user_id)
    if not job_offer:
        return PipelineResult(
            job_offer=None,
            job_match=None,
            application_draft=None,
            success=False,
            message=f"Job offer with ID {job_offer_id} not found"
        )
    
    # Step 2: Load user and build candidate profile from CV
    from app.crud import user as user_crud

    user = user_crud.get(db, user_id)
    if not user:
        return PipelineResult(
            job_offer=job_offer,
            job_match=None,
            application_draft=None,
            success=False,
            message=f"User with ID {user_id} not found",
        )

    candidate_profile = extract_profile_from_user(user)

    # Step 3: Check if match already exists
    existing_match = job_match_crud.get_by_job_offer(db, job_offer_id, user_id)
    
    if existing_match and not regenerate:
        job_match = existing_match
        message_match = "Using existing match"
    else:
        # Compute match score
        match_result = compute_match_score(job_offer, candidate_profile)
        
        # Create JobMatch record
        job_match_data = JobMatchCreate(
            job_offer_id=job_offer_id,
            score=match_result.score,
            reasons=match_result.reasons,
            skills_detected=match_result.skills_detected,
            red_flags=match_result.red_flags
        )
        
        job_match = job_match_crud.create(db, job_match_data, user_id)
        message_match = f"Match computed: {match_result.score}/100"
    
    # Step 4: Check if draft already exists
    from app.crud import application_draft as draft_crud
    existing_draft = draft_crud.get_by_job_offer(db, job_offer_id, user_id)
    
    if existing_draft and not regenerate:
        application_draft = existing_draft
        message_draft = "Using existing draft"
    else:
        # Generate application draft
        application_draft = draft_service.create_application_draft(
            db, job_offer, candidate_profile, user_id
        )
        message_draft = "Draft generated successfully"
    
    return PipelineResult(
        job_offer=job_offer,
        job_match=job_match,
        application_draft=application_draft,
        success=True,
        message=f"{message_match}. {message_draft}."
    )


def bulk_process_job_offers(
    db: Session,
    skip_existing: bool = True,
    min_score_threshold: float = 50.0
) -> list[PipelineResult]:
    """
    Process all job offers that don't have matches/drafts yet.
    
    Args:
        db: Database session
        skip_existing: If True, skip job offers that already have a match
        min_score_threshold: Only create drafts for matches above this score
    
    Returns:
        List of PipelineResult for each processed job offer
    """
    results = []
    
    # Get all job offers (tous utilisateurs)
    all_job_offers = db.query(JobOffer).order_by(JobOffer.created_at.desc()).limit(1000).all()
    
    for job_offer in all_job_offers:
        # Check if match exists
        existing_match = job_match_crud.get_by_job_offer(db, job_offer.id, job_offer.user_id)
        
        if existing_match and skip_existing:
            continue
        
        # Run pipeline
        result = run_job_offer_pipeline(job_offer.id, job_offer.user_id, db, regenerate=not skip_existing)
        
        # Only keep results above threshold
        if result.success and result.job_match.score >= min_score_threshold:
            results.append(result)
    
    return results
