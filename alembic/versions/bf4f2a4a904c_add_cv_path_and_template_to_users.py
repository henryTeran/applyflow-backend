"""add_cv_path_and_template_to_users

Revision ID: bf4f2a4a904c
Revises: 031f8c4f9e22
Create Date: 2025-12-05 00:34:46.409168

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf4f2a4a904c'
down_revision = '031f8c4f9e22'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add cv_path column
    op.add_column('users', sa.Column('cv_path', sa.String(length=500), nullable=True))
    
    # Add cover_letter_template column
    op.add_column('users', sa.Column('cover_letter_template', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove columns in reverse order
    op.drop_column('users', 'cover_letter_template')
    op.drop_column('users', 'cv_path')
