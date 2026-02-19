"""add_user_id_to_job_related_tables

Revision ID: 14143f09b0ab
Revises: a7064e1880bf
Create Date: 2025-12-05 13:06:15.879376

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14143f09b0ab'
down_revision = 'a7064e1880bf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add user_id columns to all job-related tables
    op.add_column('job_offers', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('job_matches', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('application_drafts', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('applications', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('timeline_events', sa.Column('user_id', sa.Integer(), nullable=True))
    
    # Backfill existing data with first user (or set a default)
    # This assumes you have at least one user in the database
    op.execute("UPDATE job_offers SET user_id = (SELECT id FROM users ORDER BY id LIMIT 1) WHERE user_id IS NULL")
    op.execute("UPDATE job_matches SET user_id = (SELECT id FROM users ORDER BY id LIMIT 1) WHERE user_id IS NULL")
    op.execute("UPDATE application_drafts SET user_id = (SELECT id FROM users ORDER BY id LIMIT 1) WHERE user_id IS NULL")
    op.execute("UPDATE applications SET user_id = (SELECT id FROM users ORDER BY id LIMIT 1) WHERE user_id IS NULL")
    op.execute("UPDATE timeline_events SET user_id = (SELECT id FROM users ORDER BY id LIMIT 1) WHERE user_id IS NULL")
    
    # Make columns non-nullable
    op.alter_column('job_offers', 'user_id', nullable=False)
    op.alter_column('job_matches', 'user_id', nullable=False)
    op.alter_column('application_drafts', 'user_id', nullable=False)
    op.alter_column('applications', 'user_id', nullable=False)
    op.alter_column('timeline_events', 'user_id', nullable=False)
    
    # Create foreign key constraints
    op.create_foreign_key('fk_job_offers_user_id', 'job_offers', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_job_matches_user_id', 'job_matches', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_application_drafts_user_id', 'application_drafts', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_applications_user_id', 'applications', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_timeline_events_user_id', 'timeline_events', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    
    # Create indexes
    op.create_index('ix_job_offers_user_id', 'job_offers', ['user_id'])
    op.create_index('ix_job_matches_user_id', 'job_matches', ['user_id'])
    op.create_index('ix_application_drafts_user_id', 'application_drafts', ['user_id'])
    op.create_index('ix_applications_user_id', 'applications', ['user_id'])
    op.create_index('ix_timeline_events_user_id', 'timeline_events', ['user_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_timeline_events_user_id', 'timeline_events')
    op.drop_index('ix_applications_user_id', 'applications')
    op.drop_index('ix_application_drafts_user_id', 'application_drafts')
    op.drop_index('ix_job_matches_user_id', 'job_matches')
    op.drop_index('ix_job_offers_user_id', 'job_offers')
    
    # Drop foreign key constraints
    op.drop_constraint('fk_timeline_events_user_id', 'timeline_events', type_='foreignkey')
    op.drop_constraint('fk_applications_user_id', 'applications', type_='foreignkey')
    op.drop_constraint('fk_application_drafts_user_id', 'application_drafts', type_='foreignkey')
    op.drop_constraint('fk_job_matches_user_id', 'job_matches', type_='foreignkey')
    op.drop_constraint('fk_job_offers_user_id', 'job_offers', type_='foreignkey')
    
    # Drop columns
    op.drop_column('timeline_events', 'user_id')
    op.drop_column('applications', 'user_id')
    op.drop_column('application_drafts', 'user_id')
    op.drop_column('job_matches', 'user_id')
    op.drop_column('job_offers', 'user_id')
