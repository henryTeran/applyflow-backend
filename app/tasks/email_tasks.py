"""
Email-related background tasks.
"""

from typing import List, Optional
from celery import Task
from app.celery_app import celery_app
from app.services.email_service import email_service
from app.logging_config import get_logger

logger = get_logger(__name__)


class EmailTask(Task):
    """Base task class for email tasks with error handling."""
    
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True


@celery_app.task(base=EmailTask, name="send_email")
def send_email_task(
    to_email: str,
    subject: str,
    body_html: str,
    body_plain: Optional[str] = None,
    attachments: Optional[List[str]] = None
):
    """
    Send email asynchronously.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body_html: HTML email body
        body_plain: Plain text email body (optional)
        attachments: List of file paths to attach (optional)
        
    Returns:
        Success status
    """
    try:
        logger.info("sending_email", to=to_email, subject=subject)
        
        email_service.send_email_with_attachments(
            to_email=to_email,
            subject=subject,
            body_html=body_html,
            body_plain=body_plain or body_html,
            attachments=attachments or []
        )
        
        logger.info("email_sent_successfully", to=to_email)
        return {"status": "sent", "to": to_email}
        
    except Exception as e:
        logger.error("email_send_failed", error=str(e), to=to_email)
        raise


@celery_app.task(base=EmailTask, name="send_application_email")
def send_application_email_task(
    application_id: int,
    draft_id: int
):
    """
    Send application email with draft and attachments.
    
    Args:
        application_id: Application ID
        draft_id: Draft ID with email content
        
    Returns:
        Send status
    """
    from app.database import SessionLocal
    from app.crud import application_draft, application
    
    db = SessionLocal()
    try:
        # Get draft
        draft = application_draft.get(db, id=draft_id)
        if not draft:
            raise ValueError(f"Draft {draft_id} not found")
        
        # Get application
        app = application.get(db, id=application_id)
        if not app:
            raise ValueError(f"Application {application_id} not found")
        
        logger.info(
            "sending_application_email",
            application_id=application_id,
            draft_id=draft_id
        )
        
        # Send email
        attachments = []
        if draft.cover_letter_path:
            attachments.append(draft.cover_letter_path)
        
        email_service.send_email_with_attachments(
            to_email=app.job_offer.contact_email or "hr@example.com",
            subject=draft.email_subject or f"Application for {app.job_offer.title}",
            body_html=draft.email_body or "",
            body_plain=draft.email_body or "",
            attachments=attachments
        )
        
        # Update application status
        application.update(
            db,
            db_obj=app,
            obj_in={"status": "sent", "sent_at": "now()"}
        )
        
        logger.info("application_email_sent", application_id=application_id)
        return {"status": "sent", "application_id": application_id}
        
    except Exception as e:
        logger.error("application_email_failed", error=str(e))
        raise
    finally:
        db.close()


@celery_app.task(name="send_batch_emails")
def send_batch_emails_task(email_data_list: List[dict]):
    """
    Send multiple emails in batch.
    
    Args:
        email_data_list: List of email data dictionaries
        
    Returns:
        Batch send summary
    """
    results = {
        "total": len(email_data_list),
        "sent": 0,
        "failed": 0
    }
    
    for email_data in email_data_list:
        try:
            send_email_task.delay(**email_data)
            results["sent"] += 1
        except Exception as e:
            logger.error("batch_email_failed", error=str(e))
            results["failed"] += 1
    
    return results
