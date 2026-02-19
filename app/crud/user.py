"""
CRUD operations for User model.
"""

from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create(db: Session, obj_in) -> User:
    """Create a new user."""
    # Handle both dict and Pydantic model
    if isinstance(obj_in, dict):
        user_data = obj_in
    else:
        user_data = obj_in.model_dump()
    
    # Create user instance
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """List all users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()


def update(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user information."""
    db_user = get(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Hash password if provided
    if "password" in update_data:
        update_data["hashed_password"] = update_data.pop("password")  # TODO: Hash this
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete(db: Session, user_id: int) -> bool:
    """Delete a user."""
    db_user = get(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True
