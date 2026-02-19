"""
User model - supports multi-user architecture.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User account for ApplyFlow."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User files and templates
    cv_path = Column(String(500), nullable=True)  # Deprecated, use cv_file_path
    cv_file_path = Column(String(500), nullable=True)  # Path to uploaded CV file
    cv_text = Column(Text, nullable=True)  # Extracted text from CV
    cover_letter_template = Column(Text, nullable=True)
    
    # CV sections (extracted from cv_text)
    cv_personal_info = Column(Text, nullable=True)
    cv_summary = Column(Text, nullable=True)
    cv_technical_skills = Column(Text, nullable=True)
    cv_soft_skills = Column(Text, nullable=True)
    cv_experience = Column(Text, nullable=True)
    cv_projects = Column(Text, nullable=True)
    cv_education = Column(Text, nullable=True)
    cv_awards = Column(Text, nullable=True)
    
    # Professional profile
    linkedin_url = Column(String(500), nullable=True)
    profile_summary = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
