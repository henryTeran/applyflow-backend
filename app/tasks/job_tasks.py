"""
Job processing background tasks.
"""

from celery import Task
from app.celery_app import celery_app
from app.logging_config import get_logger

logger = get_logger(__name__)


class JobTask(Task):
    """Base task class for job processing tasks."""
    
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 2}
    retry_backoff = True


@celery_app.task(base=JobTask, name="process_job_offer")
def process_job_offer_task(job_offer_id: int):
    """
    Process job offer: compute match, generate draft.
    
    Args:
        job_offer_id: Job offer ID
        
    Returns:
        Processing results
    """
    from app.database import SessionLocal
    from app.agents.pipeline_agent import run_job_offer_pipeline
    from app.crud import job_offer as job_offer_crud
    
    db = SessionLocal()
    try:
        logger.info("processing_job_offer", job_offer_id=job_offer_id)

        job_offer = job_offer_crud.get(db, job_offer_id)
        if not job_offer:
            raise ValueError(f"Job offer {job_offer_id} not found")

        result = run_job_offer_pipeline(job_offer_id, job_offer.user_id, db)
        
        logger.info(
            "job_offer_processed",
            job_offer_id=job_offer_id,
            match_score=result.job_match.score if result.job_match else None
        )
        
        return {
            "job_offer_id": job_offer_id,
            "match_score": result.job_match.score if result.job_match else None,
            "draft_id": result.application_draft.id if result.application_draft else None
        }
        
    except Exception as e:
        logger.error("job_processing_failed", error=str(e))
        raise
    finally:
        db.close()


@celery_app.task(base=JobTask, name="batch_process_jobs")
def batch_process_jobs_task(job_offer_ids: list):
    """
    Process multiple job offers in batch.
    
    Args:
        job_offer_ids: List of job offer IDs
        
    Returns:
        Batch processing summary
    """
    results = {
        "total": len(job_offer_ids),
        "processed": 0,
        "failed": 0
    }
    
    for job_id in job_offer_ids:
        try:
            process_job_offer_task.delay(job_id)
            results["processed"] += 1
        except Exception as e:
            logger.error("batch_job_failed", job_id=job_id, error=str(e))
            results["failed"] += 1
    
    return results


@celery_app.task(name="cleanup_old_drafts")
def cleanup_old_drafts_task(days_old: int = 30):
    """
    Clean up old, unused drafts.
    
    Args:
        days_old: Delete drafts older than this many days
        
    Returns:
        Cleanup summary
    """
    from datetime import datetime, timedelta
    from app.database import SessionLocal
    from app.models.application_draft import ApplicationDraft
    
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Find old, unused drafts
        old_drafts = db.query(ApplicationDraft).filter(
            ApplicationDraft.created_at < cutoff_date,
            ApplicationDraft.application_id.is_(None)  # Not linked to application
        ).all()
        
        count = len(old_drafts)
        
        for draft in old_drafts:
            db.delete(draft)
        
        db.commit()
        
        logger.info("old_drafts_cleaned", count=count, days_old=days_old)
        return {"cleaned": count, "days_old": days_old}
        
    except Exception as e:
        logger.error("cleanup_failed", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()
