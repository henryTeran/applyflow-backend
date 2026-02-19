"""
Pydantic schemas for User model.
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema with shared fields."""
    email: EmailStr
    name: str


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    cv_path: Optional[str] = None  # Deprecated, kept for backward compatibility
    cv_file_path: Optional[str] = None
    cv_text: Optional[str] = None
    cover_letter_template: Optional[str] = None
    
    # CV sections
    cv_personal_info: Optional[str] = None
    cv_summary: Optional[str] = None
    cv_technical_skills: Optional[str] = None
    cv_soft_skills: Optional[str] = None
    cv_experience: Optional[str] = None
    cv_projects: Optional[str] = None
    cv_education: Optional[str] = None
    cv_awards: Optional[str] = None
    
    linkedin_url: Optional[str] = None
    profile_summary: Optional[str] = None


class UserRead(UserBase):
    """Schema for reading user data."""
    id: int
    cv_path: Optional[str] = None  # Deprecated, kept for backward compatibility
    cv_file_path: Optional[str] = None
    cv_text: Optional[str] = None
    cover_letter_template: Optional[str] = None
    
    # CV sections
    cv_personal_info: Optional[str] = None
    cv_summary: Optional[str] = None
    cv_technical_skills: Optional[str] = None
    cv_soft_skills: Optional[str] = None
    cv_experience: Optional[str] = None
    cv_projects: Optional[str] = None
    cv_education: Optional[str] = None
    cv_awards: Optional[str] = None
    
    linkedin_url: Optional[str] = None
    profile_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserRead):
    """Schema for user in database (includes hashed password)."""
    hashed_password: str
