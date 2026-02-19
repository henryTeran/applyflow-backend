"""add_cv_and_profile_fields_to_users

Revision ID: 2031f3d10fe2
Revises: 14143f09b0ab
Create Date: 2025-12-05 14:31:25.961751

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2031f3d10fe2'
down_revision = '14143f09b0ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new CV and profile fields to users table
    op.add_column('users', sa.Column('cv_file_path', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('cv_text', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('linkedin_url', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('profile_summary', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove added columns
    op.drop_column('users', 'profile_summary')
    op.drop_column('users', 'linkedin_url')
    op.drop_column('users', 'cv_text')
    op.drop_column('users', 'cv_file_path')
