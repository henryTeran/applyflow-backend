"""
File upload endpoints for CV/resume and other documents.
"""

import os
import uuid
from typing import List
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import FileResponse
import aiofiles

from app.config import settings
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    "documents": {".pdf", ".doc", ".docx", ".txt", ".rtf"},
    "images": {".jpg", ".jpeg", ".png", ".gif"},
    "all": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".jpg", ".jpeg", ".png", ".gif"}
}


def get_upload_path(user_id: int, category: str = "documents") -> Path:
    """
    Get upload directory path for a user.
    
    Args:
        user_id: User ID
        category: File category (documents, images, etc.)
        
    Returns:
        Path object for upload directory
    """
    upload_dir = Path(settings.upload_path) / str(user_id) / category
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def is_allowed_file(filename: str, category: str = "documents") -> bool:
    """
    Check if file extension is allowed.
    
    Args:
        filename: Original filename
        category: File category
        
    Returns:
        True if file is allowed
    """
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS.get(category, ALLOWED_EXTENSIONS["all"])


def generate_safe_filename(original_filename: str) -> str:
    """
    Generate a safe, unique filename.
    
    Args:
        original_filename: Original uploaded filename
        
    Returns:
        Safe filename with UUID prefix
    """
    ext = Path(original_filename).suffix.lower()
    safe_name = Path(original_filename).stem
    # Remove special characters
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ('-', '_'))
    # Generate unique filename
    unique_id = str(uuid.uuid4())[:8]
    return f"{unique_id}_{safe_name}{ext}"


@router.post("/upload/cv", status_code=status.HTTP_201_CREATED)
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload CV/resume file.
    
    Args:
        file: Uploaded file
        current_user: Current authenticated user
        
    Returns:
        Upload confirmation with file path
        
    Raises:
        HTTPException: If file is invalid or too large
    """
    # Validate file size
    contents = await file.read()
    if len(contents) > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_upload_size / (1024*1024)}MB"
        )
    
    # Validate file type
    if not is_allowed_file(file.filename, "documents"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS['documents'])}"
        )
    
    # Generate safe filename
    filename = generate_safe_filename(file.filename)
    upload_dir = get_upload_path(current_user.id, "cv")
    file_path = upload_dir / filename
    
    # Save file
    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(contents)
        
        logger.info(
            "file_uploaded",
            user_id=current_user.id,
            filename=filename,
            original_filename=file.filename,
            size=len(contents),
            category="cv"
        )
        
        return {
            "message": "File uploaded successfully",
            "filename": filename,
            "original_filename": file.filename,
            "size": len(contents),
            "path": str(file_path.relative_to(settings.upload_path))
        }
    except Exception as e:
        logger.error("file_upload_failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )


@router.post("/upload/document", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload general document.
    
    Args:
        file: Uploaded file
        current_user: Current authenticated user
        
    Returns:
        Upload confirmation with file path
    """
    # Similar logic to upload_cv but for general documents
    contents = await file.read()
    
    if len(contents) > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size"
        )
    
    if not is_allowed_file(file.filename, "documents"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed"
        )
    
    filename = generate_safe_filename(file.filename)
    upload_dir = get_upload_path(current_user.id, "documents")
    file_path = upload_dir / filename
    
    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(contents)
        
        logger.info(
            "document_uploaded",
            user_id=current_user.id,
            filename=filename,
            size=len(contents)
        )
        
        return {
            "message": "Document uploaded successfully",
            "filename": filename,
            "original_filename": file.filename,
            "size": len(contents),
            "path": str(file_path.relative_to(settings.upload_path))
        }
    except Exception as e:
        logger.error("document_upload_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


@router.get("/files/list")
async def list_files(
    category: str = "documents",
    current_user: User = Depends(get_current_user)
):
    """
    List uploaded files for current user.
    
    Args:
        category: File category to list
        current_user: Current authenticated user
        
    Returns:
        List of uploaded files
    """
    upload_dir = get_upload_path(current_user.id, category)
    
    if not upload_dir.exists():
        return {"files": []}
    
    files = []
    for file_path in upload_dir.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "path": str(file_path.relative_to(settings.upload_path))
            })
    
    return {"files": files}


@router.get("/files/download/{category}/{filename}")
async def download_file(
    category: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download a file.
    
    Args:
        category: File category
        filename: File name
        current_user: Current authenticated user
        
    Returns:
        File download response
        
    Raises:
        HTTPException: If file not found
    """
    file_path = get_upload_path(current_user.id, category) / filename
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Security check: ensure file is in user's directory
    try:
        file_path.relative_to(get_upload_path(current_user.id, category))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )


@router.delete("/files/delete/{category}/{filename}")
async def delete_file(
    category: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a file.
    
    Args:
        category: File category
        filename: File name
        current_user: Current authenticated user
        
    Returns:
        Deletion confirmation
        
    Raises:
        HTTPException: If file not found
    """
    file_path = get_upload_path(current_user.id, category) / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Security check
    try:
        file_path.relative_to(get_upload_path(current_user.id, category))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        os.remove(file_path)
        logger.info(
            "file_deleted",
            user_id=current_user.id,
            filename=filename,
            category=category
        )
        return {"message": "File deleted successfully"}
    except Exception as e:
        logger.error("file_deletion_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )
