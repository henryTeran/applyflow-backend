"""
Users API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os

from app.api.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.crud import user as crud
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user."""
    # Check if user with email already exists
    existing_user = crud.get_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    return crud.create(db, user)


@router.get("/", response_model=List[UserRead])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all users."""
    return crud.list_users(db, skip=skip, limit=limit)


@router.get("/me", response_model=UserRead)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    """
    return current_user


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific user by ID."""
    user = crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/me", response_model=UserRead)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    user = crud.update(db, current_user.id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user information (admin)."""
    user = crud.update(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/debug-cv-extraction-public")
async def debug_cv_extraction_public(
    file: UploadFile = File(...)
):
    """
    PUBLIC DEBUG endpoint: Upload CV and see raw extracted text (NO AUTH REQUIRED).
    """
    from app.services.cv_service import extract_text_from_pdf
    import logging
    import time
    logger = logging.getLogger(__name__)
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    os.makedirs("uploads/cv", exist_ok=True)
    file_path = f"uploads/cv/debug_{int(time.time())}_{file.filename}"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    raw_text = extract_text_from_pdf(file_path)
    
    if not raw_text:
        return {"error": "Text extraction failed", "raw_text": None}
    
    return {
        "file_path": file_path,
        "text_length": len(raw_text),
        "raw_text": raw_text,  # Full raw text from PyPDF2
        "first_500_chars": raw_text[:500],
        "message": "This is the RAW text extracted by PyPDF2 (no AI processing)"
    }


@router.post("/debug-cv-extraction")
async def debug_cv_extraction(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    DEBUG endpoint: Upload CV and see raw extracted text (no AI processing).
    """
    from app.services.cv_service import extract_text_from_pdf
    import logging
    logger = logging.getLogger(__name__)
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    os.makedirs("uploads/cv", exist_ok=True)
    file_path = f"uploads/cv/debug_{current_user.id}_{file.filename}"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    raw_text = extract_text_from_pdf(file_path)
    
    if not raw_text:
        return {"error": "Text extraction failed", "raw_text": None}
    
    return {
        "file_path": file_path,
        "text_length": len(raw_text),
        "raw_text": raw_text,  # Full raw text from PyPDF2
        "first_500_chars": raw_text[:500],
        "message": "This is the RAW text extracted by PyPDF2 (no AI processing)"
    }


@router.post("/upload-cv")
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload user CV (PDF only), extract text, restructure with AI, and extract sections.
    """
    from app.services.cv_service import extract_text_from_pdf, restructure_cv_text_with_ai
    from app.services.cv_parser_sections import extract_cv_sections
    from app.config import settings
    import logging
    logger = logging.getLogger(__name__)
    
    # Vérifier que c'est un PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Créer le dossier uploads s'il n'existe pas
    os.makedirs("uploads/cv", exist_ok=True)
    
    # Sauvegarder avec un nom unique
    file_path = f"uploads/cv/{current_user.id}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Extraire le texte du PDF
    raw_cv_text = extract_text_from_pdf(file_path)
    if not raw_cv_text:
        logger.warning("Could not extract text from CV")
        current_user.cv_file_path = file_path
        current_user.cv_path = file_path
        current_user.cv_text = None
        db.commit()
        db.refresh(current_user)
        
        return {
            "file_path": file_path,
            "text_extracted": False,
            "text_length": 0,
            "restructured": False,
            "sections_extracted": False,
            "message": "CV uploaded but text extraction failed"
        }
    
    logger.info(f"Extracted {len(raw_cv_text)} characters from CV")
    
    # Restructurer le texte avec l'IA si disponible
    openai_key = getattr(settings, 'OPENAI_API_KEY', None)
    cv_text = restructure_cv_text_with_ai(raw_cv_text, openai_key)
    restructured = cv_text != raw_cv_text
    
    if restructured:
        logger.info(f"CV text restructured with AI ({len(cv_text)} chars)")
    
    # Extraire les sections du CV
    sections = extract_cv_sections(cv_text)
    sections_count = len([v for v in sections.values() if v])
    
    # Mettre à jour le user avec le texte restructuré et les sections
    current_user.cv_file_path = file_path
    current_user.cv_path = file_path  # Backward compatibility
    current_user.cv_text = cv_text
    
    # Stocker les sections
    current_user.cv_personal_info = sections.get("personal_info")
    current_user.cv_summary = sections.get("summary")
    current_user.cv_technical_skills = sections.get("technical_skills")
    current_user.cv_soft_skills = sections.get("soft_skills")
    current_user.cv_experience = sections.get("experience")
    current_user.cv_projects = sections.get("projects")
    current_user.cv_education = sections.get("education")
    current_user.cv_awards = sections.get("awards")
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "file_path": file_path,
        "text_extracted": True,
        "text_length": len(cv_text),
        "restructured": restructured,
        "sections_extracted": sections_count > 0,
        "sections_count": sections_count,
        "message": f"CV uploaded successfully ({sections_count} sections extracted)" if sections_count > 0 else "CV uploaded successfully"
    }


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Delete a user."""
    success = crud.delete(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None
