"""
Webhook endpoints for receiving updates from job portals.
"""

import hmac
import hashlib
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Header, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.config import settings
from app.logging_config import get_logger
from app import crud

router = APIRouter()
logger = get_logger(__name__)


class WebhookPayload(BaseModel):
    """Generic webhook payload schema."""
    event_type: str = Field(..., description="Type of event (status_update, interview_scheduled, etc.)")
    application_id: Optional[int] = Field(None, description="Internal application ID if known")
    external_id: Optional[str] = Field(None, description="External reference ID from portal")
    data: dict = Field(..., description="Event-specific data")
    timestamp: str = Field(..., description="Event timestamp")


class ApplicationStatusUpdate(BaseModel):
    """Application status update payload."""
    status: str
    message: Optional[str] = None
    updated_at: str


class InterviewScheduled(BaseModel):
    """Interview scheduled payload."""
    interview_date: str
    interview_type: str  # phone, video, onsite
    location: Optional[str] = None
    interviewer: Optional[str] = None
    notes: Optional[str] = None


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str = None
) -> bool:
    """
    Verify webhook signature using HMAC.
    
    Args:
        payload: Raw request body
        signature: Signature from header
        secret: Webhook secret key
        
    Returns:
        True if signature is valid
    """
    if not secret:
        secret = settings.secret_key
    
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


@router.post("/webhook/application-update")
async def application_update_webhook(
    request: Request,
    payload: WebhookPayload,
    x_webhook_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Receive application status updates from job portals.
    
    Args:
        request: FastAPI request object
        payload: Webhook payload
        x_webhook_signature: Signature header for verification
        db: Database session
        
    Returns:
        Acknowledgment response
        
    Raises:
        HTTPException: If signature is invalid
    """
    # Verify signature if provided
    if x_webhook_signature:
        body = await request.body()
        if not verify_webhook_signature(body, x_webhook_signature):
            logger.warning("invalid_webhook_signature", event_type=payload.event_type)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    logger.info(
        "webhook_received",
        event_type=payload.event_type,
        application_id=payload.application_id,
        external_id=payload.external_id
    )
    
    try:
        # Find application
        if payload.application_id:
            application = crud.application.get(db, id=payload.application_id)
        elif payload.external_id:
            # Find by external reference (would need to add this field to model)
            application = None  # TODO: implement lookup by external_id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No application identifier provided"
            )
        
        if not application:
            logger.warning(
                "application_not_found",
                application_id=payload.application_id,
                external_id=payload.external_id
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Handle different event types
        if payload.event_type == "status_update":
            status_data = ApplicationStatusUpdate(**payload.data)
            
            # Update application status
            crud.application.update(
                db,
                db_obj=application,
                obj_in={"status": status_data.status}
            )
            
            # Create timeline event
            crud.timeline_event.create(
                db,
                obj_in={
                    "application_id": application.id,
                    "event_type": "status_change",
                    "title": f"Status updated to: {status_data.status}",
                    "description": status_data.message
                }
            )
            
        elif payload.event_type == "interview_scheduled":
            interview_data = InterviewScheduled(**payload.data)
            
            # Create timeline event for interview
            crud.timeline_event.create(
                db,
                obj_in={
                    "application_id": application.id,
                    "event_type": "interview",
                    "title": f"Interview scheduled - {interview_data.interview_type}",
                    "description": f"Date: {interview_data.interview_date}\n"
                                 f"Type: {interview_data.interview_type}\n"
                                 f"Location: {interview_data.location or 'TBD'}\n"
                                 f"Notes: {interview_data.notes or 'None'}",
                    "scheduled_at": interview_data.interview_date
                }
            )
            
            # Update application status
            crud.application.update(
                db,
                db_obj=application,
                obj_in={"status": "interview"}
            )
            
        elif payload.event_type == "rejection":
            # Update application status
            crud.application.update(
                db,
                db_obj=application,
                obj_in={"status": "rejected"}
            )
            
            # Create timeline event
            crud.timeline_event.create(
                db,
                obj_in={
                    "application_id": application.id,
                    "event_type": "status_change",
                    "title": "Application rejected",
                    "description": payload.data.get("message", "No reason provided")
                }
            )
            
        elif payload.event_type == "offer":
            # Update application status
            crud.application.update(
                db,
                db_obj=application,
                obj_in={"status": "offer"}
            )
            
            # Create timeline event
            crud.timeline_event.create(
                db,
                obj_in={
                    "application_id": application.id,
                    "event_type": "offer_received",
                    "title": "Job offer received!",
                    "description": payload.data.get("details", "Offer details in email")
                }
            )
        
        logger.info(
            "webhook_processed",
            event_type=payload.event_type,
            application_id=application.id
        )
        
        return {
            "status": "success",
            "message": "Webhook processed successfully",
            "application_id": application.id
        }
        
    except Exception as e:
        logger.error("webhook_processing_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )


@router.post("/webhook/test")
async def test_webhook(payload: dict):
    """
    Test webhook endpoint for development.
    
    Args:
        payload: Test payload
        
    Returns:
        Echo response
    """
    logger.info("test_webhook_received", payload=payload)
    return {
        "status": "received",
        "payload": payload,
        "message": "Test webhook processed"
    }


@router.get("/webhook/signature-example")
async def webhook_signature_example():
    """
    Get example of how to generate webhook signatures.
    
    Returns:
        Signature generation example
    """
    example_payload = '{"event_type":"status_update","data":{"status":"interview"}}'
    example_secret = "your-webhook-secret"
    
    signature = hmac.new(
        example_secret.encode(),
        example_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return {
        "message": "How to generate webhook signatures",
        "example": {
            "payload": example_payload,
            "secret": example_secret,
            "signature": signature,
            "algorithm": "HMAC-SHA256"
        },
        "usage": {
            "header": "X-Webhook-Signature",
            "value": signature
        },
        "python_code": '''
import hmac
import hashlib

secret = "your-webhook-secret"
payload = '{"event_type":"status_update",...}'

signature = hmac.new(
    secret.encode(),
    payload.encode(),
    hashlib.sha256
).hexdigest()

headers = {"X-Webhook-Signature": signature}
'''
    }
